from __future__ import annotations

from typing import Optional

from textual import events
from textual.widgets import Input


class VimInput(Input):
    """Input widget that supports a tiny subset of Vim-like commands.

    Minimal and purpose-built: normal mode toggled with Esc; supports a few
    motions and delete/change operators used in tests.
    """

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._vim_normal = False
        self._pending_operator: Optional[str] = None
        self._pending_text_object: Optional[str] = None
        self._pending_count: int = 0
        self._count_active = False

    async def handle_key(self, event: events.Key) -> bool:  # type: ignore[override]
        key = event.key
        if self._vim_normal:
            if key == "escape":
                event.stop(); event.prevent_default(); self._reset_pending(); return True
            if key == ".":
                event.stop(); event.prevent_default(); return True
            if self._handle_normal_mode_key(event):
                return True
        else:
            if key == "escape":
                self._enter_normal_mode(); event.stop(); event.prevent_default(); return True
        return await super().handle_key(event)

    async def _on_key(self, event: events.Key) -> None:  # type: ignore[override]
        if self._vim_normal and self._handle_normal_mode_key(event):
            return
        await super()._on_key(event)

    def _handle_normal_mode_key(self, event: events.Key) -> bool:
        key = event.key
        if self._consume_text_object(key, event):
            return True
        if self._accumulate_count(key, event):
            return True
        if self._enter_insert_or_append(key, event):
            return True
        if self._init_change_all(key, event):
            return True
        if self._init_operator(key, event):
            return True
        if self._pending_operator:
            return self._handle_operator_key(key, event)
        return self._motion_or_edit(key, event)

    # --- helpers to reduce branching ---
    def _consume_text_object(self, key: str, event: events.Key) -> bool:
        if self._pending_text_object is None:
            return False
        kind = self._pending_text_object + key
        self._apply_text_object(kind)
        event.stop(); event.prevent_default()
        return True

    def _accumulate_count(self, key: str, event: events.Key) -> bool:
        if not key.isdigit():
            return False
        if not self._count_active and key == "0":
            self._apply_motion("0", 1)
        else:
            self._pending_count = self._pending_count * 10 + int(key)
            self._count_active = True
        event.stop(); event.prevent_default()
        return True

    def _enter_insert_or_append(self, key: str, event: events.Key) -> bool:
        if self._pending_operator is not None:
            return False
        if key in {"i", "I"}:
            self._vim_normal = False
            if key == "I":
                self.cursor_position = 0
            event.stop(); event.prevent_default(); self._reset_pending()
            return True
        if key == "a":
            self._move_cursor(1); self._vim_normal = False
            event.stop(); event.prevent_default(); self._reset_pending()
            return True
        return False

    def _init_change_all(self, key: str, event: events.Key) -> bool:
        if self._pending_operator is None and key == "C":
            self._pending_operator = "c"
            self._apply_operator_motion("$", self._get_count())
            event.stop(); event.prevent_default()
            return True
        return False

    def _init_operator(self, key: str, event: events.Key) -> bool:
        if self._pending_operator is None and key in {"d", "c"}:
            self._pending_operator = key
            event.stop(); event.prevent_default()
            return True
        return False

    def _handle_operator_key(self, key: str, event: events.Key) -> bool:
        if key in {"w", "b", "h", "l", "0", "$"}:
            self._apply_operator_motion(key, self._get_count())
            event.stop(); event.prevent_default()
            return True
        if key in {"i", "a"}:
            self._pending_text_object = key
            event.stop(); event.prevent_default()
            return True
        self._reset_pending()
        return False

    def _motion_or_edit(self, key: str, event: events.Key) -> bool:
        if key not in {"h", "l", "0", "$", "w", "b", "x"}:
            return False
        if key == "h": self._move_cursor(-1)
        elif key == "l": self._move_cursor(1)
        elif key == "0": self.cursor_position = 0
        elif key == "$": self.cursor_position = len(self.value)
        elif key == "w": self.cursor_position = self._motion_word_forward(self.cursor_position, self._get_count())
        elif key == "b": self.cursor_position = self._motion_word_backward(self.cursor_position, self._get_count())
        elif key == "x": self._delete_under_cursor()
        event.stop(); event.prevent_default(); self._reset_pending()
        return True

    def _enter_normal_mode(self) -> None:
        self._vim_normal = True; self._reset_pending()

    def _move_cursor(self, delta: int) -> None:
        self.cursor_position = max(0, min(len(self.value), self.cursor_position + delta))

    def _delete_under_cursor(self) -> None:
        pos = self.cursor_position
        if pos < len(self.value):
            self.value = self.value[:pos] + self.value[pos + 1 :]

    def _get_count(self) -> int:
        return self._pending_count or 1

    def _reset_pending(self) -> None:
        self._pending_operator = None; self._pending_text_object = None; self._pending_count = 0; self._count_active = False

    def _apply_motion(self, motion: str, count: int) -> None:
        if motion == "0": self.cursor_position = 0
        elif motion == "$": self.cursor_position = len(self.value)
        elif motion == "h": self._move_cursor(-count)
        elif motion == "l": self._move_cursor(count)
        elif motion == "w": self.cursor_position = self._motion_word_forward(self.cursor_position, count)
        elif motion == "b": self.cursor_position = self._motion_word_backward(self.cursor_position, count)

    def _apply_operator_motion(self, motion: str, count: int) -> None:
        start = self.cursor_position; end = start
        if motion == "h": end = max(0, start - count)
        elif motion == "l": end = min(len(self.value), start + count)
        elif motion == "w": end = self._motion_word_forward(start, count)
        elif motion == "b": end = self._motion_word_backward(start, count)
        elif motion == "0": end = 0
        elif motion == "$": end = len(self.value)
        self._execute_operator(start, end)

    def _apply_text_object(self, obj: str) -> None:
        start, end = self._text_object_range(obj)
        if start is None or end is None: self._reset_pending(); return
        self._execute_operator(start, end)

    def _execute_operator(self, start: int, end: int) -> None:
        if not self._pending_operator: self._reset_pending(); return
        a, b = sorted((start, end))
        if a == b: self._reset_pending(); return
        if self._pending_operator == "d":
            self.value = self.value[:a] + self.value[b:]; self.cursor_position = min(a, len(self.value))
        elif self._pending_operator == "c":
            self.value = self.value[:a] + self.value[b:]; self.cursor_position = min(a, len(self.value)); self._vim_normal = False
        self._reset_pending()

    def _text_object_range(self, obj: str) -> tuple[Optional[int], Optional[int]]:
        if obj not in {"iw", "aw"}: return (None, None)
        start, end = self._word_bounds(self.cursor_position)
        if start is None or end is None: return (None, None)
        if obj == "aw":
            while end < len(self.value) and self.value[end].isspace(): end += 1
            while start > 0 and self.value[start - 1].isspace(): start -= 1
        return (start, end)

    def _word_bounds(self, pos: int) -> tuple[Optional[int], Optional[int]]:
        text = self.value
        if not text: return (None, None)
        cursor = min(max(pos, 0), len(text) - 1)
        if not self._is_word_char(text[cursor]):
            if cursor > 0 and self._is_word_char(text[cursor - 1]): cursor -= 1
            else: return (None, None)
        start = cursor
        while start > 0 and self._is_word_char(text[start - 1]): start -= 1
        end = cursor + 1
        while end < len(text) and self._is_word_char(text[end]): end += 1
        return start, end

    def _motion_word_forward(self, pos: int, count: int) -> int:
        cursor = pos
        for _ in range(count): cursor = self._skip_word_forward(cursor); cursor = self._skip_whitespace_forward(cursor)
        return min(cursor, len(self.value))

    def _motion_word_backward(self, pos: int, count: int) -> int:
        cursor = pos
        for _ in range(count): cursor = self._skip_whitespace_backward(cursor); cursor = self._skip_word_backward(cursor)
        return max(cursor, 0)

    def _skip_word_forward(self, pos: int) -> int:
        text = self.value; cursor = pos; length = len(text)
        if cursor < length and text[cursor].isspace(): cursor = self._skip_whitespace_forward(cursor)
        while cursor < length and self._is_word_char(text[cursor]): cursor += 1
        return cursor

    def _skip_whitespace_forward(self, pos: int) -> int:
        text = self.value; cursor = pos
        while cursor < len(text) and text[cursor].isspace(): cursor += 1
        return cursor

    def _skip_whitespace_backward(self, pos: int) -> int:
        text = self.value; cursor = max(0, pos - 1)
        while cursor > 0 and text[cursor].isspace(): cursor -= 1
        if cursor == 0 and text[:1].isspace(): return 0
        if cursor < len(text) and text[cursor].isspace(): cursor = max(cursor - 1, 0)
        return cursor

    def _skip_word_backward(self, pos: int) -> int:
        text = self.value; cursor = min(pos, len(text))
        if cursor > 0 and (cursor == len(text) or text[cursor].isspace()): cursor = self._skip_whitespace_backward(cursor)
        while cursor > 0 and self._is_word_char(text[cursor - 1]): cursor -= 1
        return cursor

    @staticmethod
    def _is_word_char(ch: str) -> bool:
        return ch.isalnum() or ch == "_"
