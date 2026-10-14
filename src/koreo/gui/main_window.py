"""Application shell sharing one project and playback session between views."""

from dataclasses import replace
from fractions import Fraction
from pathlib import Path
from tempfile import TemporaryDirectory
from uuid import uuid4

from PySide6.QtCore import QEvent, QObject, QSize, Qt, Signal
from PySide6.QtGui import QAction, QCloseEvent, QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QFileDialog,
    QApplication,
    QDialog,
    QDialogButtonBox,
    QDoubleSpinBox,
    QFormLayout,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QProgressBar,
    QSlider,
    QSizePolicy,
    QStackedWidget,
    QSpinBox,
    QTabBar,
    QTextEdit,
    QPlainTextEdit,
    QToolBar,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from koreo.audio import AudioProbe, AudioSource, WaveformExtractor
from koreo.application.session import ProjectSession
from koreo.domain.calibration import BeatCalibration, parse_bpm
from koreo.domain.choreography import (
    ChoreographyEditError,
    create_move,
    delete_move,
    ripple_later_moves,
    trim_edited_move,
    update_move,
)
from koreo.domain.models import Move, Project
from koreo.domain.structure import rebase_structure
from koreo.export.creation_sheet import (
    CreationSheetExportError,
    export_creation_sheet_pdf,
)
from koreo.gui.bpm_dialog import BpmDialog
from koreo.gui.choreography_panel import ChoreographyPanel, MoveEditRequest
from koreo.gui.icons import IconRole, semantic_icon
from koreo.gui.sheet import SheetView
from koreo.gui.structure_panel import StructurePanel
from koreo.gui.timeline import TimelineView
from koreo.gui.waveform import WaveformWidget
from koreo.playback import PlaybackController
from koreo.persistence import (
    LoadedProject,
    ProjectFileError,
    load_project,
    save_project,
)
from koreo.presentation.mapping import build_sheet, build_timeline
from koreo.settings import APPEARANCE


class MainWindow(QMainWindow):
    """Host the audio-backed Structure workspace for one project."""

    play_pause_requested = Signal()

    def __init__(
        self, project: Project, *, prompt_to_save_on_close: bool = True
    ) -> None:
        super().__init__()
        self._prompt_to_save_on_close = prompt_to_save_on_close
        self.session = ProjectSession(project)
        self.project_path: Path | None = None
        self._extraction_directory: TemporaryDirectory[str] = TemporaryDirectory(
            prefix="koreo-project-"
        )
        self.audio_source: AudioSource | None = None
        self.tempo_bpm = Fraction(120)
        self._probe = AudioProbe(self)
        self._probe.succeeded.connect(self._audio_ready)
        self._probe.failed.connect(self._audio_failed)
        self._waveform_extractor = WaveformExtractor(self)
        self._waveform_extractor.succeeded.connect(self._waveform_ready)
        self._waveform_extractor.failed.connect(self._waveform_failed)
        self.playback = PlaybackController(self)
        self.playback.position_changed.connect(self._position_changed)
        self.playback.duration_changed.connect(self._duration_changed)
        self.playback.state_changed.connect(self._playback_state_changed)
        self.playback.failed.connect(self._playback_failed)
        application = QApplication.instance()
        assert application is not None
        application.installEventFilter(self)
        self.play_pause_requested.connect(self._toggle_playback)
        self.timeline_view = TimelineView(build_timeline(project))
        self.sheet_view = SheetView(build_sheet(project))
        self.structure_panel = StructurePanel(project)
        self.structure_panel.project_changed.connect(self._structure_project_changed)
        self.structure_panel.undo_requested.connect(self._undo)
        self.structure_panel.redo_requested.connect(self._redo)
        self.structure_panel.anchor_block_requested.connect(
            self._anchor_structure_block
        )
        self.structure_panel.position_requested.connect(self._seek_to_structure_beat)
        self.choreography_panel = ChoreographyPanel(project)
        self.choreography_panel.edit_requested.connect(self._choreography_edit)
        self.choreography_panel.details_requested.connect(self._choreography_details)
        self.choreography_panel.delete_requested.connect(self._delete_choreography_move)
        self.choreography_panel.undo_requested.connect(self._undo)
        self.choreography_panel.redo_requested.connect(self._redo)
        self.choreography_panel.position_requested.connect(self._seek_to_structure_beat)
        self.choose_song_button = self._icon_button(
            IconRole.CHOOSE_AUDIO, "Choose audio track"
        )
        self.choose_song_button.clicked.connect(self._choose_song)
        self.song_label = QLabel("No song selected")
        self.song_label.setWordWrap(True)
        self.tap_bpm_button = self._icon_button(IconRole.TAP_BPM, "Tap BPM")
        self.tap_bpm_button.setEnabled(False)
        self.tap_bpm_button.clicked.connect(self._open_bpm_dialog)
        self.bpm_edit = QDoubleSpinBox()
        self.bpm_edit.setAccessibleName("Manual BPM")
        self.bpm_edit.setRange(1.0, 999.99)
        self.bpm_edit.setDecimals(2)
        self.bpm_edit.setSingleStep(0.5)
        self.bpm_edit.setValue(120.0)
        self.bpm_edit.setMaximumWidth(76)
        self.bpm_edit.editingFinished.connect(self._manual_bpm_changed)
        self.project_name_edit = QLineEdit(project.name)
        self.project_name_edit.setAccessibleName("Project name")
        self.project_name_edit.setMinimumWidth(260)
        self.project_name_edit.setMaximumWidth(420)
        self.project_name_edit.editingFinished.connect(self._project_name_changed)
        self.project_name_edit.returnPressed.connect(self.project_name_edit.clearFocus)
        self.song_settings_button = self._icon_button(
            IconRole.SONG_SETTINGS, "Advanced song settings"
        )

        self.song_settings_dialog = QDialog(self)
        self.song_settings_dialog.setWindowTitle("Advanced song settings")
        self.song_settings_dialog.setModal(True)
        settings_layout = QFormLayout(self.song_settings_dialog)
        self.count_origin_edit = QSpinBox()
        self.count_origin_edit.setRange(-4096, 4096)
        self.count_origin_edit.setValue(int(project.count_origin))
        self.count_origin_edit.valueChanged.connect(self._count_origin_changed)
        settings_layout.addRow("Count origin:", self.count_origin_edit)
        self.count_group_spin = QSpinBox()
        self.count_group_spin.setRange(1, 64)
        self.count_group_spin.setValue(project.default_count_group)
        self.count_group_spin.valueChanged.connect(self._count_group_changed)
        settings_layout.addRow("Default count group:", self.count_group_spin)
        settings_buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        settings_buttons.rejected.connect(self.song_settings_dialog.reject)
        settings_layout.addRow(settings_buttons)
        self.song_settings_button.clicked.connect(self.song_settings_dialog.open)

        self.transport = QWidget()
        self.transport.setSizePolicy(
            QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed
        )
        transport_layout = QVBoxLayout(self.transport)
        transport_layout.setContentsMargins(0, 0, 0, 0)
        controls = QHBoxLayout()
        self.play_button = self._icon_button(IconRole.PLAY, "Play")
        self.play_button.clicked.connect(self._toggle_playback)
        self.stop_button = self._icon_button(IconRole.STOP, "Stop")
        self.stop_button.clicked.connect(self.playback.stop)
        self.seek_slider = QSlider(Qt.Orientation.Horizontal)
        self.seek_slider.setRange(0, 0)
        self.seek_slider.sliderMoved.connect(self.playback.seek)
        self.time_label = QLabel("0:00.000 / 0:00.000")
        self.time_label.setFixedWidth(
            self.time_label.fontMetrics().horizontalAdvance("99:59.999 / 99:59.999")
        )
        self.time_label.setAlignment(
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
        )
        controls.addWidget(self.play_button)
        controls.addWidget(self.stop_button)
        controls.addStretch(1)
        controls.addWidget(self.time_label)
        transport_layout.addLayout(controls)

        self.waveform = WaveformWidget()
        self.waveform.set_bpm(float(self.tempo_bpm))
        self.waveform.set_count_group(project.default_count_group)
        self.waveform.seek_requested.connect(self._seek_from_waveform)
        transport_layout.addWidget(self.waveform)
        self.setup_tools = QWidget()
        calibration_controls = QHBoxLayout(self.setup_tools)
        calibration_controls.setContentsMargins(0, 0, 0, 0)
        self.processing_indicator = QProgressBar()
        self.processing_indicator.setRange(0, 0)
        self.processing_indicator.setFormat("Processing song…")
        self.processing_indicator.setMaximumWidth(170)
        self.processing_indicator.setVisible(False)
        self.zoom_out_button = self._icon_button(IconRole.ZOOM_OUT, "Zoom waveform out")
        self.zoom_out_button.clicked.connect(self.waveform.zoom_out)
        self.zoom_in_button = self._icon_button(IconRole.ZOOM_IN, "Zoom waveform in")
        self.zoom_in_button.clicked.connect(self.waveform.zoom_in)
        self.zoom_fit_button = self._icon_button(
            IconRole.ZOOM_FIT, "Fit the full waveform"
        )
        self.zoom_fit_button.clicked.connect(self.waveform.zoom_to_fit)
        self.follow_button = self._icon_button(
            IconRole.FOLLOW_PLAYHEAD, "Follow playhead", checkable=True
        )
        self.follow_button.setChecked(True)
        self.follow_button.setToolTip("Keep the playhead at a fixed offset")
        self.follow_button.toggled.connect(self.waveform.set_follow_playhead)
        self.waveform.follow_changed.connect(self.follow_button.setChecked)
        self.section_labels_toggle = self._icon_button(
            IconRole.SECTION_LABELS, "Show section labels", checkable=True
        )
        self.section_labels_toggle.setChecked(APPEARANCE.show_waveform_section_labels)
        self.section_labels_toggle.setToolTip(
            "Show song-structure section names on the waveform"
        )
        self.section_labels_toggle.toggled.connect(
            self.waveform.set_show_structure_labels
        )
        self.anchor_button = self._icon_button(
            IconRole.WAVEFORM_ANCHOR, "Set playhead as grid Anchor"
        )
        self.anchor_button.clicked.connect(self._set_anchor)
        self.anchor_label = QLabel("—")
        self.anchor_label.setToolTip("Grid Anchor time")
        calibration_controls.addWidget(self.choose_song_button)
        calibration_controls.addWidget(self.song_label, 1)
        calibration_controls.addWidget(self.processing_indicator)
        calibration_controls.addWidget(self._tool_separator())
        calibration_controls.addWidget(self.zoom_out_button)
        calibration_controls.addWidget(self.zoom_in_button)
        calibration_controls.addWidget(self.zoom_fit_button)
        calibration_controls.addWidget(self.follow_button)
        calibration_controls.addWidget(self.section_labels_toggle)
        calibration_controls.addWidget(self._tool_separator())
        calibration_controls.addWidget(QLabel("BPM:"))
        calibration_controls.addWidget(self.bpm_edit)
        calibration_controls.addWidget(self.tap_bpm_button)
        calibration_controls.addWidget(self.anchor_button)
        calibration_controls.addWidget(self.anchor_label)
        calibration_controls.addWidget(self._tool_separator())
        calibration_controls.addWidget(self.song_settings_button)
        transport_layout.addWidget(self.setup_tools)
        self.transport.setVisible(True)
        central = QWidget()
        layout = QVBoxLayout(central)
        self.workspace_tabs = QTabBar()
        self.workspace_tabs.setExpanding(False)
        self.workspace_tabs.addTab("Setup")
        self.workspace_tabs.addTab("Choreography")
        layout.addWidget(self.workspace_tabs)
        layout.addWidget(self.transport)
        self.workspace_stack = QStackedWidget()
        self.workspace_stack.addWidget(self.structure_panel)
        self.workspace_stack.addWidget(self.choreography_panel)
        layout.addWidget(self.workspace_stack, 1)
        self.workspace_tabs.currentChanged.connect(self.workspace_stack.setCurrentIndex)
        self.workspace_tabs.currentChanged.connect(self._workspace_changed)
        if project.moves:
            self.workspace_tabs.setCurrentIndex(1)
        self.undo_shortcut = QShortcut(
            QKeySequence(QKeySequence.StandardKey.Undo), self
        )
        self.undo_shortcut.setContext(Qt.ShortcutContext.WindowShortcut)
        self.undo_shortcut.activated.connect(self._undo)
        self.redo_shortcut = QShortcut(QKeySequence("Ctrl+Shift+Z"), self)
        self.redo_shortcut.setContext(Qt.ShortcutContext.WindowShortcut)
        self.redo_shortcut.activated.connect(self._redo)
        self.setCentralWidget(central)
        self._build_file_ui()
        self._update_window_title()
        self.resize(1100, 700)

    @property
    def project(self) -> Project:
        """Return the application session's authoritative project."""

        return self.session.project

    @property
    def dirty(self) -> bool:
        return self.session.dirty

    def _icon_button(
        self, role: IconRole, name: str, *, checkable: bool = False
    ) -> QToolButton:
        """Create a compact control whose meaning is not tied to its artwork."""

        button = QToolButton(self)
        button.setIcon(semantic_icon(button, role))
        button.setIconSize(QSize(20, 20))
        button.setAccessibleName(name)
        button.setToolTip(name)
        button.setCheckable(checkable)
        return button

    def _tool_separator(self) -> QFrame:
        separator = QFrame(self)
        separator.setFrameShape(QFrame.Shape.VLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        return separator

    def _build_file_ui(self) -> None:
        file_menu = self.menuBar().addMenu("&File")
        assert file_menu is not None
        self.open_action = QAction("&Open…", self)
        self.open_action.setShortcut(QKeySequence.StandardKey.Open)
        self.open_action.triggered.connect(self._open_project)
        self.save_action = QAction("&Save", self)
        self.save_action.setShortcut(QKeySequence.StandardKey.Save)
        self.save_action.triggered.connect(self._save)
        self.save_as_action = QAction("Save &As…", self)
        self.save_as_action.setShortcut(QKeySequence.StandardKey.SaveAs)
        self.save_as_action.triggered.connect(self._save_as)
        self.export_creation_sheet_action = QAction("Export Creation Sheet PDF…", self)
        self.export_creation_sheet_action.triggered.connect(self._export_creation_sheet)
        self.exit_action = QAction("E&xit", self)
        self.exit_action.setShortcut(QKeySequence.StandardKey.Quit)
        self.exit_action.triggered.connect(self.close)
        file_menu.addActions([self.open_action, self.save_action, self.save_as_action])
        file_menu.addAction(self.export_creation_sheet_action)
        file_menu.addSeparator()
        file_menu.addAction(self.exit_action)

        self.project_toolbar = QToolBar("Project", self)
        self.project_toolbar.setObjectName("project_toolbar")
        self.project_toolbar.setMovable(False)
        self.project_toolbar.setFloatable(False)
        self.project_toolbar.setIconSize(QSize(20, 20))
        self.addToolBar(self.project_toolbar)
        self.open_action.setIcon(
            semantic_icon(self.project_toolbar, IconRole.OPEN_PROJECT)
        )
        self.save_action.setIcon(
            semantic_icon(self.project_toolbar, IconRole.SAVE_PROJECT)
        )
        self.project_toolbar.addAction(self.open_action)
        self.project_toolbar.addAction(self.save_action)
        toolbar_spacer = QWidget(self.project_toolbar)
        toolbar_spacer.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred
        )
        self.project_toolbar.addWidget(toolbar_spacer)
        self.project_toolbar.addWidget(QLabel("Project:", self.project_toolbar))
        self.project_toolbar.addWidget(self.project_name_edit)

    def _choose_song(self) -> None:
        selected, _ = QFileDialog.getOpenFileName(
            self, "Choose song", "", "Audio files (*.mp3 *.wav)"
        )
        if selected:
            self.load_song(Path(selected))

    def _export_creation_sheet(self) -> None:
        suggested = (
            self.project_path.with_suffix(".creation-sheet.pdf").name
            if self.project_path is not None
            else f"{self.project.name}.creation-sheet.pdf"
        )
        selected, _ = QFileDialog.getSaveFileName(
            self,
            "Export Creation Sheet PDF",
            suggested,
            "PDF files (*.pdf)",
        )
        if not selected:
            return
        path = Path(selected)
        if path.suffix.lower() != ".pdf":
            path = path.with_suffix(".pdf")
        project_filename = (
            self.project_path.name
            if self.project_path is not None
            else "Unsaved project"
        )
        try:
            export_creation_sheet_pdf(
                self.project,
                path,
                project_filename=project_filename,
            )
        except (CreationSheetExportError, OSError) as error:
            QMessageBox.critical(self, "Creation sheet export failed", str(error))

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:  # noqa: N802
        """Reserve Space for main-window playback across focused controls."""

        del watched
        application = QApplication.instance()
        assert application is None or isinstance(application, QApplication)
        if (
            event.type() == QEvent.Type.KeyPress
            and event.key() == Qt.Key.Key_Space  # type: ignore[attr-defined]
            and self.isActiveWindow()
            and application is not None
            and application.activeModalWidget() is None
        ):
            focused = application.focusWidget()
            if isinstance(
                focused,
                (QLineEdit, QTextEdit, QPlainTextEdit, QSpinBox, QDoubleSpinBox),
            ):
                return False
            if not event.isAutoRepeat():  # type: ignore[attr-defined]
                self.play_pause_requested.emit()
            return True
        return False

    def load_song(self, path: Path) -> None:
        """Validate a selected song without replacing the last valid source."""

        self.choose_song_button.setEnabled(False)
        self.song_label.setText(f"Checking {path.name}…")
        self._probe.probe(path)

    def _audio_ready(self, source: object) -> None:
        assert isinstance(source, AudioSource)
        self.audio_source = source
        self._commit_project(
            replace(self.project, calibration=None), "Choose audio track"
        )
        self.waveform.set_peaks(())
        self.waveform.set_anchor(None)
        self.waveform.zoom_to_fit()
        self.waveform.set_follow_playhead(True)
        self.anchor_label.setText("—")
        self.song_label.setText(source.display_name)
        self.choose_song_button.setEnabled(True)
        self.tap_bpm_button.setEnabled(True)
        self.playback.load(source.path)
        self.processing_indicator.setVisible(True)
        self._waveform_extractor.extract(source.path)
        self._mark_dirty()

    def _audio_failed(self, message: str) -> None:
        if self.audio_source is None:
            self.song_label.setText(message)
        else:
            self.song_label.setText(
                f"{self.audio_source.display_name} — new selection failed: {message}"
            )
        self.choose_song_button.setEnabled(True)

    def _open_bpm_dialog(self) -> None:
        if self.audio_source is None:
            return
        dialog = BpmDialog(self.audio_source, self)
        if dialog.exec() and dialog.result_bpm is not None:
            self.tempo_bpm = dialog.result_bpm
            self.bpm_edit.setValue(float(self.tempo_bpm))
            self.waveform.set_bpm(float(self.tempo_bpm))
            self._update_calibration_bpm()
            self._mark_dirty()

    def _manual_bpm_changed(self) -> None:
        self.tempo_bpm = parse_bpm(f"{self.bpm_edit.value():.2f}")
        self.waveform.set_bpm(float(self.tempo_bpm))
        self._update_calibration_bpm()
        self._mark_dirty()

    def _project_name_changed(self) -> None:
        name = self.project_name_edit.text().strip()
        if not name:
            self.project_name_edit.setText(self.project.name)
            return
        if name == self.project.name:
            self.project_name_edit.setText(name)
            return
        self._commit_project(replace(self.project, name=name), "Rename project")
        self.project_name_edit.setText(name)

    def _count_origin_changed(self, origin: int) -> None:
        self._commit_project(
            replace(self.project, count_origin=Fraction(origin)), "Change count origin"
        )

    def _count_group_changed(self, group_size: int) -> None:
        self._commit_project(
            replace(self.project, default_count_group=group_size),
            "Change default count group",
        )

    def _refresh_count_views(self) -> None:
        timeline_model = build_timeline(self.project)
        sheet_model = build_sheet(self.project)
        self.timeline_view.model = timeline_model
        self.timeline_view.canvas.model = timeline_model
        self.timeline_view.canvas.update()
        self.sheet_view.model = sheet_model
        self.sheet_view.canvas.model = sheet_model
        self.sheet_view.canvas.update()
        self.structure_panel.set_project(self.project)
        self.choreography_panel.set_project(self.project)
        self.waveform.set_count_group(self.project.default_count_group)

    def _commit_project(self, project: Project, label: str) -> bool:
        """Commit one validated project transition through shared history."""

        if not self.session.replace(project, label):
            return False
        self._refresh_count_views()
        self._refresh_structure_mapping()
        self._update_window_title()
        return True

    def _undo(self) -> None:
        if not self.session.undo():
            return
        self._refresh_count_views()
        self._refresh_structure_mapping()
        self._update_window_title()

    def _redo(self) -> None:
        if not self.session.redo():
            return
        self._refresh_count_views()
        self._refresh_structure_mapping()
        self._update_window_title()

    def _workspace_changed(self, index: int) -> None:
        """Expose setup tools only in Setup and compact the shared waveform."""

        choreography = index == 1
        self.setup_tools.setVisible(not choreography)
        self.waveform.set_simplified(choreography)
        self.waveform.setFixedHeight(24 if choreography else 150)
        self.transport.setMinimumHeight(0)
        self.transport.setMaximumHeight(16_777_215)
        transport_height = 67 if choreography else self.transport.sizeHint().height()
        self.transport.setFixedHeight(transport_height)
        self.transport.updateGeometry()
        central = self.centralWidget()
        central_layout = central.layout() if central is not None else None
        if central_layout is not None:
            central_layout.invalidate()
            central_layout.activate()

    def _choreography_edit(self, request: object) -> None:
        assert isinstance(request, MoveEditRequest)
        previous_ids = {move.id for move in self.project.moves}
        existing = next(
            (move for move in self.project.moves if move.id == request.move_id), None
        )
        if request.action == "create":
            edited = Move(
                f"move-{uuid4().hex}",
                request.track_id,
                request.start,
                request.duration,
                "New move",
            )
        else:
            assert existing is not None
            edited = replace(
                existing,
                track_id=request.track_id,
                start=request.start,
                duration=request.duration,
            )
        project = self._resolve_move_edit(edited, request.move_id, request.release_beat)
        if project is None:
            return
        self._commit_project(project, f"{request.action.title()} choreography move")
        selected_id = request.move_id
        if selected_id is None:
            selected_id = next(
                move.id for move in project.moves if move.id not in previous_ids
            )
        self.choreography_panel.canvas.selected_move_id = selected_id
        self.choreography_panel._selection_changed(selected_id)
        if request.action == "create":
            self.choreography_panel.canvas.begin_label_edit(selected_id)

    def _choreography_details(self, details: object) -> None:
        assert isinstance(details, tuple) and len(details) == 5
        move_id, label, notes, start, duration = details
        assert isinstance(move_id, str)
        assert isinstance(label, str)
        assert notes is None or isinstance(notes, str)
        assert isinstance(start, Fraction)
        assert isinstance(duration, Fraction)
        existing = next(move for move in self.project.moves if move.id == move_id)
        edited = replace(
            existing,
            label=label or existing.label,
            notes=notes,
            start=start,
            duration=duration,
        )
        project = self._resolve_move_edit(edited, move_id, start)
        if project is not None:
            self._commit_project(project, "Edit choreography move details")

    def _delete_choreography_move(self, move_id: str) -> None:
        self._commit_project(
            delete_move(self.project, move_id), "Delete choreography move"
        )

    def _resolve_move_edit(
        self, edited: Move, original_id: str | None, release_beat: Fraction
    ) -> Project | None:
        try:
            if original_id is None:
                return create_move(
                    self.project,
                    edited.track_id,
                    edited.start,
                    edited.duration,
                    label=edited.label,
                    move_id=edited.id,
                )
            return update_move(
                self.project,
                original_id,
                start=edited.start,
                duration=edited.duration,
                label=edited.label,
                notes=edited.notes,
            )
        except ChoreographyEditError as error:
            if "overlap" not in str(error).lower():
                QMessageBox.warning(self, "Move edit rejected", str(error))
                return None
        message = QMessageBox(self)
        message.setWindowTitle("Choreography conflict")
        message.setText("This edit overlaps another move on the same track.")
        cancel = message.addButton("Cancel", QMessageBox.ButtonRole.RejectRole)
        trim = message.addButton("Trim edited move", QMessageBox.ButtonRole.ActionRole)
        shift = message.addButton(
            "Shift later moves", QMessageBox.ButtonRole.AcceptRole
        )
        message.exec()
        clicked = message.clickedButton()
        if clicked is cancel:
            return None
        if clicked is trim:
            try:
                project = trim_edited_move(
                    self.project,
                    original_id,
                    edited.track_id,
                    edited.start,
                    edited.duration,
                    release_beat,
                    label=edited.label,
                )
                if original_id is not None:
                    project = update_move(
                        project,
                        original_id,
                        label=edited.label,
                        notes=edited.notes,
                    )
                return project
            except ChoreographyEditError as error:
                QMessageBox.warning(self, "Move edit rejected", str(error))
                return None
        if clicked is shift:
            return ripple_later_moves(self.project, edited, original_id=original_id)
        return None

    def _structure_project_changed(self, project: object) -> None:
        assert isinstance(project, Project)
        self._commit_project(project, "Edit song structure")

    def _anchor_structure_block(self, block_id: str) -> None:
        calibration = self.project.calibration
        if calibration is None:
            self.structure_panel.status.setText(
                "Set the grid Anchor on the waveform first."
            )
            return
        block = next(region for region in self.project.regions if region.id == block_id)
        anchor_seconds = calibration.anchor_seconds
        self._commit_project(
            rebase_structure(self.project, block.start), "Align Structure to Anchor"
        )
        assert self.project.calibration is not None
        assert self.project.calibration.anchor_seconds == anchor_seconds
        self.structure_panel.status.setText("Selected block starts at the grid Anchor.")

    def _seek_to_structure_beat(self, beat: object) -> None:
        assert isinstance(beat, Fraction)
        calibration = self.project.calibration
        if calibration is None:
            self.structure_panel.status.setText(
                "Set the grid Anchor before seeking by structure."
            )
            return
        milliseconds = round(calibration.seconds_at(beat) * 1000)
        self.playback.seek(max(0, milliseconds))

    def _toggle_playback(self) -> None:
        if self.playback.is_playing:
            self.playback.pause()
        else:
            self.playback.play()

    def _position_changed(self, position_ms: int) -> None:
        if not self.seek_slider.isSliderDown():
            self.seek_slider.setValue(position_ms)
        self.waveform.set_position(position_ms)
        if self.project.calibration is None:
            self.structure_panel.set_playhead_beat(None)
            self.choreography_panel.set_playhead_beat(None)
        else:
            beat = self.project.calibration.beat_at(Fraction(position_ms, 1000))
            self.structure_panel.set_playhead_beat(beat)
            self.choreography_panel.set_playhead_beat(beat)
        self.time_label.setText(
            f"{_format_ms(position_ms)} / {_format_ms(self.playback.duration)}"
        )

    def _duration_changed(self, duration_ms: int) -> None:
        self.seek_slider.setMaximum(max(duration_ms, 0))
        self.waveform.set_duration(duration_ms)
        self._position_changed(self.playback.position)

    def _playback_state_changed(self, state: str) -> None:
        playing = state == "playing"
        name = "Pause" if playing else "Play"
        role = IconRole.PAUSE if playing else IconRole.PLAY
        self.play_button.setIcon(semantic_icon(self.play_button, role))
        self.play_button.setAccessibleName(name)
        self.play_button.setToolTip(name)

    def _playback_failed(self, message: str) -> None:
        self.song_label.setText(f"Playback error: {message}")

    def _waveform_ready(self, peaks: object) -> None:
        assert isinstance(peaks, tuple)
        self.waveform.set_peaks(peaks)
        self.processing_indicator.setVisible(False)
        if self.audio_source is not None:
            self.song_label.setText(self.audio_source.display_name)

    def _waveform_failed(self, message: str) -> None:
        self.processing_indicator.setVisible(False)
        self.song_label.setText(message)

    def _set_anchor(self) -> None:
        anchor_ms = self.waveform.position_ms
        calibration = BeatCalibration(
            bpm=self.tempo_bpm,
            anchor_seconds=Fraction(anchor_ms, 1000),
        )
        self._commit_project(
            replace(self.project, calibration=calibration), "Set grid Anchor"
        )
        self.waveform.set_anchor(anchor_ms)
        self.anchor_label.setText(_format_ms(anchor_ms))
        self._refresh_structure_mapping()
        self._mark_dirty()

    def _update_calibration_bpm(self) -> None:
        if self.project.calibration is not None:
            self._commit_project(
                replace(
                    self.project,
                    calibration=self.project.calibration.with_bpm(self.tempo_bpm),
                ),
                "Change tempo",
            )
            self._refresh_structure_mapping()

    def _refresh_structure_mapping(self) -> None:
        calibration = self.project.calibration
        if calibration is None:
            self.waveform.set_structure_bands(())
            return
        bands = tuple(
            (
                round(calibration.seconds_at(region.start) * 1000),
                round(calibration.seconds_at(region.end) * 1000),
                region.color or "#bfdbfe",
                region.label,
            )
            for region in self.project.regions
            if region.parent_id is None
        )
        self.waveform.set_structure_bands(bands)

    def _mark_dirty(self) -> None:
        self.session.mark_external_change()
        self._update_window_title()

    def _set_clean(self) -> None:
        self.session.mark_clean()
        self._update_window_title()

    def _update_window_title(self) -> None:
        marker = "*" if self.dirty else ""
        name = self.project_path.name if self.project_path else self.project.name
        self.setWindowTitle(f"Koreo — {name}{marker}")

    def _save(self) -> bool:
        if self.project_path is None:
            return self._save_as()
        try:
            save_project(
                self.project_path,
                self.project,
                self.tempo_bpm,
                self.audio_source,
                self.waveform.peaks,
            )
        except (ProjectFileError, OSError) as error:
            QMessageBox.critical(self, "Save failed", str(error))
            return False
        self._set_clean()
        return True

    def _save_as(self) -> bool:
        selected, _ = QFileDialog.getSaveFileName(
            self,
            "Save Koreo project",
            str(self.project_path or Path(f"{self.project.name}.kro")),
            "Koreo projects (*.kro)",
        )
        if not selected:
            return False
        path = Path(selected)
        if path.suffix.lower() != ".kro":
            path = path.with_suffix(".kro")
        previous = self.project_path
        self.project_path = path
        self.project_name_edit.setText(self.project.name)
        if not self._save():
            self.project_path = previous
            self._update_window_title()
            return False
        return True

    def _open_project(self) -> None:
        if not self._confirm_discard_changes():
            return
        selected, _ = QFileDialog.getOpenFileName(
            self, "Open Koreo project", "", "Koreo projects (*.kro)"
        )
        if not selected:
            return
        extraction = Path(self._extraction_directory.name) / uuid4().hex
        try:
            loaded = load_project(Path(selected), extraction)
        except ProjectFileError as error:
            QMessageBox.critical(self, "Open failed", str(error))
            return
        self._apply_loaded_project(loaded, Path(selected))

    def _apply_loaded_project(self, loaded: LoadedProject, path: Path) -> None:
        self.playback.stop()
        self.session.load(loaded.project)
        self.tempo_bpm = loaded.tempo_bpm
        self.project_path = path
        self.project_name_edit.setText(self.project.name)
        self.bpm_edit.setValue(float(self.tempo_bpm))
        self.waveform.set_bpm(float(self.tempo_bpm))
        self.count_origin_edit.blockSignals(True)
        self.count_origin_edit.setValue(int(self.project.count_origin))
        self.count_origin_edit.blockSignals(False)
        self.count_group_spin.blockSignals(True)
        self.count_group_spin.setValue(self.project.default_count_group)
        self.count_group_spin.blockSignals(False)
        self._refresh_count_views()
        calibration = self.project.calibration
        anchor_ms = (
            None if calibration is None else round(calibration.anchor_seconds * 1000)
        )
        self.waveform.set_anchor(anchor_ms)
        self.anchor_label.setText("—" if anchor_ms is None else _format_ms(anchor_ms))
        self._refresh_structure_mapping()
        self.audio_source = loaded.audio_source
        if loaded.audio_source is None:
            self.song_label.setText("No song selected")
            self.tap_bpm_button.setEnabled(False)
            self.waveform.set_peaks(())
        else:
            source = loaded.audio_source
            self.song_label.setText(source.display_name)
            self.tap_bpm_button.setEnabled(True)
            self.playback.load(source.path)
            if loaded.waveform_peaks:
                self.waveform.set_peaks(loaded.waveform_peaks)
                self.processing_indicator.setVisible(False)
                self.song_label.setText(source.display_name)
            else:
                self.processing_indicator.setVisible(True)
                self._waveform_extractor.extract(source.path)
        if loaded.migrated:
            self.session.mark_external_change()
            self._update_window_title()
        else:
            self._set_clean()
        self.workspace_tabs.setCurrentIndex(1 if self.project.moves else 0)

    def _seek_from_waveform(self, position_ms: int) -> None:
        self.playback.seek(position_ms)
        # Qt may report the media position asynchronously while stopped. Keep
        # the visible playhead and immediate Anchor action deterministic.
        self._position_changed(position_ms)

    def _confirm_discard_changes(self) -> bool:
        if not self.dirty or not self._prompt_to_save_on_close:
            return True
        answer = QMessageBox.warning(
            self,
            "Unsaved changes",
            "Save changes before continuing?",
            QMessageBox.StandardButton.Save
            | QMessageBox.StandardButton.Discard
            | QMessageBox.StandardButton.Cancel,
            QMessageBox.StandardButton.Save,
        )
        if answer == QMessageBox.StandardButton.Cancel:
            return False
        if answer == QMessageBox.StandardButton.Save:
            return self._save()
        return True

    def closeEvent(self, event: QCloseEvent) -> None:  # noqa: N802
        if not self._confirm_discard_changes():
            event.ignore()
            return
        self.playback.stop()
        self._extraction_directory.cleanup()
        event.accept()


def _format_ms(milliseconds: int) -> str:
    minutes, remainder = divmod(max(milliseconds, 0), 60_000)
    seconds, millis = divmod(remainder, 1000)
    return f"{minutes}:{seconds:02d}.{millis:03d}"
