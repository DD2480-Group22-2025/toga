from __future__ import annotations

import warnings
from typing import Any

from travertino.constants import (  # noqa: F401
    BOLD,
    BOTTOM,
    CENTER,
    COLUMN,
    CURSIVE,
    FANTASY,
    HIDDEN,
    ITALIC,
    JUSTIFY,
    LEFT,
    LTR,
    MONOSPACE,
    NONE,
    NORMAL,
    OBLIQUE,
    RIGHT,
    ROW,
    RTL,
    SANS_SERIF,
    SERIF,
    SMALL_CAPS,
    SYSTEM,
    TOP,
    TRANSPARENT,
    VISIBLE,
)
from travertino.declaration import BaseStyle, Choices
from travertino.layout import BaseBox
from travertino.node import Node
from travertino.size import BaseIntrinsicSize

from toga.fonts import (
    FONT_STYLES,
    FONT_VARIANTS,
    FONT_WEIGHTS,
    SYSTEM_DEFAULT_FONT_SIZE,
    SYSTEM_DEFAULT_FONTS,
    Font,
)

# Make sure deprecation warnings are shown by default
warnings.filterwarnings("default", category=DeprecationWarning)

######################################################################
# Display
######################################################################

PACK = "pack"

######################################################################
# Declaration choices
######################################################################

# Define here, since they're not available in Travertino 0.3.0
START = "start"
END = "end"
# Used in backwards compatibility section below
ALIGNMENT = "alignment"
ALIGN_ITEMS = "align_items"

DISPLAY_CHOICES = Choices(PACK, NONE)
VISIBILITY_CHOICES = Choices(VISIBLE, HIDDEN)
DIRECTION_CHOICES = Choices(ROW, COLUMN)
ALIGN_ITEMS_CHOICES = Choices(START, CENTER, END)
# Deprecated, but maintained for backwards compatibility with Toga <= 0.4.8
ALIGNMENT_CHOICES = Choices(LEFT, RIGHT, TOP, BOTTOM, CENTER)

SIZE_CHOICES = Choices(NONE, integer=True)
FLEX_CHOICES = Choices(number=True)

MARGIN_CHOICES = Choices(integer=True)

TEXT_ALIGN_CHOICES = Choices(LEFT, RIGHT, CENTER, JUSTIFY)
TEXT_DIRECTION_CHOICES = Choices(RTL, LTR)

COLOR_CHOICES = Choices(color=True)
BACKGROUND_COLOR_CHOICES = Choices(TRANSPARENT, color=True)

FONT_FAMILY_CHOICES = Choices(*SYSTEM_DEFAULT_FONTS, string=True)
FONT_STYLE_CHOICES = Choices(*FONT_STYLES)
FONT_VARIANT_CHOICES = Choices(*FONT_VARIANTS)
FONT_WEIGHT_CHOICES = Choices(*FONT_WEIGHTS)
FONT_SIZE_CHOICES = Choices(integer=True)


class Pack(BaseStyle):
    class Box(BaseBox):
        pass

    class IntrinsicSize(BaseIntrinsicSize):
        pass

    _depth = -1

    def _debug(self, *args: str) -> None:  # pragma: no cover
        print("    " * self.__class__._depth, *args)

    @property
    def _hidden(self) -> bool:
        """Does this style declaration define an object that should be hidden."""
        return self.visibility == HIDDEN

    #######################################################
    # Backwards compatibility for Toga <= 0.4.8
    #######################################################

    # Pack.alignment is still an actual property, despite being deprecated, so we need
    # to suppress deprecation warnings when reapply is called.
    def reapply(self, *args, **kw):
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", category=DeprecationWarning)
            super().reapply(*args, **kw)

    DEPRECATED_PROPERTIES = {
        # Map each deprecated property name to its replacement.
        # alignment / align_items is handled separately.
        "padding": "margin",
        "padding_top": "margin_top",
        "padding_right": "margin_right",
        "padding_bottom": "margin_bottom",
        "padding_left": "margin_left",
    }

    @classmethod
    def _update_property_name(cls, name):
        if new_name := cls.DEPRECATED_PROPERTIES.get(name):
            cls._warn_deprecated(name, new_name, stacklevel=4)
            name = new_name

        return name

    @staticmethod
    def _warn_deprecated(old_name, new_name, stacklevel=3):
        msg = f"Pack.{old_name} is deprecated; use {new_name} instead"
        warnings.warn(msg, DeprecationWarning, stacklevel=stacklevel)

    # Dot lookup

    def __getattribute__(self, name):
        if name in {
            "direction",
            "text_direction",
            "_warn_deprecated",
            "_update_property_name",
        }:
            return super().__getattribute__(name)

        # Align_items and alignment are paired. Both can never be set at the same time;
        # if one is requested, and the other one is set, compute the requested value
        # from the one that is set.
        if name == ALIGN_ITEMS and (alignment := super().__getattribute__(ALIGNMENT)):
            if alignment == CENTER:
                return CENTER

            if self.direction == ROW:
                if alignment == TOP:
                    return START
                if alignment == BOTTOM:
                    return END

                # No remaining valid combinations
                return None

            # direction must be COLUMN
            if alignment == LEFT:
                return START if self.text_direction == LTR else END
            if alignment == RIGHT:
                return START if self.text_direction == RTL else END

            # No remaining valid combinations
            return None

        if name == ALIGNMENT:
            # Warn, whether it's set or not.
            self._warn_deprecated(ALIGNMENT, ALIGN_ITEMS)

            if align_items := super().__getattribute__(ALIGN_ITEMS):
                if align_items == START:
                    if self.direction == COLUMN:
                        return LEFT if self.text_direction == LTR else RIGHT
                    return TOP  # for ROW

                if align_items == END:
                    if self.direction == COLUMN:
                        return RIGHT if self.text_direction == LTR else LEFT
                    return BOTTOM  # for ROW

                # Only CENTER remains
                return CENTER

        return super().__getattribute__(self._update_property_name(name))

    def __setattr__(self, name, value):
        # Only one of these can be set at a time.
        if name == ALIGN_ITEMS:
            super().__delattr__(ALIGNMENT)
        elif name == ALIGNMENT:
            self._warn_deprecated(ALIGNMENT, ALIGN_ITEMS)
            super().__delattr__(ALIGN_ITEMS)

        super().__setattr__(self._update_property_name(name), value)

    def __delattr__(self, name):
        # If one of the two is being deleted, delete the other also.
        if name == ALIGN_ITEMS:
            super().__delattr__(ALIGNMENT)
        elif name == ALIGNMENT:
            self._warn_deprecated(ALIGNMENT, ALIGN_ITEMS)
            super().__delattr__(ALIGN_ITEMS)

        super().__delattr__(self._update_property_name(name))

    # Index notation

    def __getitem__(self, name):
        return getattr(self, name.replace("-", "_"))

    def __setitem__(self, name, value):
        setattr(self, name.replace("-", "_"), value)

    def __delitem__(self, name):
        delattr(self, name.replace("-", "_"))

    #######################################################
    # End backwards compatibility
    #######################################################

    def apply(self, prop: str, value: object) -> None:
        if self._applicator:
            if prop == "text_align":
                if value is None:
                    if self.text_direction == RTL:
                        value = RIGHT
                    else:
                        value = LEFT
                self._applicator.set_text_align(value)
            elif prop == "text_direction":
                if self.text_align is None:
                    self._applicator.set_text_align(RIGHT if value == RTL else LEFT)
            elif prop == "color":
                self._applicator.set_color(value)
            elif prop == "background_color":
                self._applicator.set_background_color(value)
            elif prop == "visibility":
                if value == VISIBLE:
                    # If visibility is being set to VISIBLE, look up the chain to see if
                    # an ancestor is hidden.
                    widget = self._applicator.widget
                    while widget := widget.parent:
                        if widget.style._hidden:
                            value = HIDDEN
                            break

                self._applicator.set_hidden(value == HIDDEN)
            elif prop in (
                "font_family",
                "font_size",
                "font_style",
                "font_variant",
                "font_weight",
            ):
                self._applicator.set_font(
                    Font(
                        self.font_family,
                        self.font_size,
                        style=self.font_style,
                        variant=self.font_variant,
                        weight=self.font_weight,
                    )
                )
            else:
                # Any other style change will cause a change in layout geometry,
                # so perform a refresh.
                self._applicator.refresh()

    def layout(self, node: Node, viewport: Any) -> None:
        # self._debug("=" * 80)
        # self._debug(
        #     f"Layout root {node}, available {viewport.width}x{viewport.height}"
        # )
        self.__class__._depth = -1

        self._layout_node(
            node,
            alloc_width=viewport.width,
            alloc_height=viewport.height,
            use_all_height=True,  # root node uses all height
            use_all_width=True,  # root node uses all width
        )
        node.layout.content_top = node.style.margin_top
        node.layout.content_bottom = node.style.margin_bottom

        node.layout.content_left = node.style.margin_left
        node.layout.content_right = node.style.margin_right

    def _layout_node(
        self,
        node: Node,
        alloc_width: int,
        alloc_height: int,
        use_all_width: bool,
        use_all_height: bool,
    ) -> None:
        self.__class__._depth += 1
        # self._debug(
        #     f"COMPUTE LAYOUT for {node} available "
        #     f"{alloc_width}{'+' if use_all_width else ''}"
        #     " x "
        #     f"{alloc_height}{'+' if use_all_height else ''}"
        # )

        # Establish available width
        if self.width != NONE:
            # If width is specified, use it
            available_width = self.width
            min_width = self.width
            # self._debug(f"SPECIFIED WIDTH {self.width}")
        else:
            # If no width is specified, assume we're going to use all
            # the available width. If there is an intrinsic width,
            # use it to make sure the width is at least the amount specified.
            available_width = max(
                0, (alloc_width - self.margin_left - self.margin_right)
            )
            # self._debug(f"INITIAL {available_width=}")
            if node.intrinsic.width is not None:
                # self._debug(f"INTRINSIC WIDTH {node.intrinsic.width}")
                try:
                    min_width = node.intrinsic.width.value
                    available_width = max(available_width, min_width)
                except AttributeError:
                    available_width = node.intrinsic.width
                    min_width = node.intrinsic.width

                # self._debug(f"ADJUSTED {available_width=}")
            else:
                # self._debug(f"AUTO {available_width=}")
                min_width = 0

        # Establish available height
        if self.height != NONE:
            # If height is specified, use it.
            available_height = self.height
            min_height = self.height
            # self._debug(f"SPECIFIED HEIGHT {self.height}")
        else:
            available_height = max(
                0,
                alloc_height - self.margin_top - self.margin_bottom,
            )
            # self._debug(f"INITIAL {available_height=}")
            if node.intrinsic.height is not None:
                # self._debug(f"INTRINSIC HEIGHT {node.intrinsic.height}")
                try:
                    min_height = node.intrinsic.height.value
                    available_height = max(available_height, min_height)
                except AttributeError:
                    available_height = node.intrinsic.height
                    min_height = node.intrinsic.height

                # self._debug(f"ADJUSTED {available_height=}")
            else:
                # self._debug(f"AUTO {available_height=}")
                min_height = 0

        if node.children:
            if self.direction == COLUMN:
                min_width, width, min_height, height = self._layout_column_children(
                    node,
                    available_width=available_width,
                    available_height=available_height,
                    use_all_height=use_all_height,
                    use_all_width=use_all_width,
                )
            else:
                min_width, width, min_height, height = self._layout_row_children(
                    node,
                    available_width=available_width,
                    available_height=available_height,
                    use_all_height=use_all_height,
                    use_all_width=use_all_width,
                )
            # self._debug(f"HAS CHILDREN {min_width=} {width=} {min_height=} {height=}")
        else:
            width = available_width
            height = available_height
            # self._debug(f"NO CHILDREN {min_width=} {width=} {min_height=} {height=}")

        # If an explicit width/height was given, that specification
        # overrides the width/height evaluated by the layout of children
        if self.width != NONE:
            width = self.width
            min_width = width
        if self.height != NONE:
            height = self.height
            min_height = height

        # self._debug(f"FINAL SIZE {min_width}x{min_height} {width}x{height}")
        node.layout.content_width = int(width)
        node.layout.content_height = int(height)

        node.layout.min_content_width = int(min_width)
        node.layout.min_content_height = int(min_height)

        # self._debug("END LAYOUT", node, node.layout)
        self.__class__._depth -= 1

    def _layout_row_children(
        self,
        node: Node,
        available_width: int,
        available_height: int,
        use_all_width: bool,
        use_all_height: bool,
    ) -> tuple[int, int, int, int]:
        # self._debug(f"LAYOUT ROW CHILDREN {available_width=} {available_height=}")
        # Pass 1: Lay out all children with a hard-specified width, or an
        # intrinsic non-flexible width. While iterating, collect the flex
        # total of remaining elements.
        flex_total = 0
        min_flex = 0
        width = 0
        min_width = 0
        remaining_width = available_width
        for child in node.children:
            # self._debug(f"PASS 1 {child}")
            if child.style.width != NONE:
                # self._debug(f"- fixed width {child.style.width}")
                child.style._layout_node(
                    child,
                    alloc_width=remaining_width,
                    alloc_height=available_height,
                    use_all_width=False,
                    use_all_height=child.style.direction == ROW,
                )
                child_content_width = child.layout.content_width
                # It doesn't matter how small the children can be laid out;
                # we have an intrinsic size; so don't use min_content_width
                min_child_content_width = child.layout.content_width
            elif child.intrinsic.width is not None:
                if hasattr(child.intrinsic.width, "value"):
                    if child.style.flex:
                        # self._debug(f"- intrinsic flex width {child.intrinsic.width}")
                        flex_total += child.style.flex
                        # Final child content size will be computed in pass 2, after the
                        # amount of flexible space is known. For now, set an initial
                        # content height based on the intrinsic size, which will be the
                        # minimum possible allocation.
                        child_content_width = child.intrinsic.width.value
                        min_child_content_width = child.intrinsic.width.value
                        min_flex += (
                            child.style.margin_left
                            + child.intrinsic.width.value
                            + child.style.margin_right
                        )
                    else:
                        # self._debug(f"- intrinsic non-flex {child.intrinsic.width=}")
                        child.style._layout_node(
                            child,
                            alloc_width=0,
                            alloc_height=available_height,
                            use_all_width=False,
                            use_all_height=child.style.direction == ROW,
                        )
                        child_content_width = child.layout.content_width
                        # It doesn't matter how small the children can be laid out;
                        # we have an intrinsic size; so don't use min_content_width
                        min_child_content_width = child.layout.content_width
                else:
                    # self._debug(f"- intrinsic {child.intrinsic.width=}")
                    child.style._layout_node(
                        child,
                        alloc_width=remaining_width,
                        alloc_height=available_height,
                        use_all_width=False,
                        use_all_height=child.style.direction == ROW,
                    )
                    child_content_width = child.layout.content_width
                    # It doesn't matter how small the children can be laid out;
                    # we have an intrinsic size; so don't use min_content_width
                    min_child_content_width = child.layout.content_width
            else:
                if child.style.flex:
                    # self._debug("- unspecified flex width")
                    flex_total += child.style.flex
                    # Final child content size will be computed in pass 2, after the
                    # amount of flexible space is known. For now, use 0 as the minimum,
                    # as that's the best hint the widget style can give.
                    child_content_width = 0
                    min_child_content_width = 0
                else:
                    # self._debug("- unspecified non-flex width")
                    child.style._layout_node(
                        child,
                        alloc_width=remaining_width,
                        alloc_height=available_height,
                        use_all_width=False,
                        use_all_height=child.style.direction == ROW,
                    )
                    child_content_width = child.layout.content_width
                    min_child_content_width = child.layout.min_content_width

            child_width = (
                child.style.margin_left + child_content_width + child.style.margin_right
            )
            width += child_width
            remaining_width -= child_width

            min_child_width = (
                child.style.margin_left
                + min_child_content_width
                + child.style.margin_right
            )
            min_width += min_child_width

            # self._debug(f"  {min_child_width=} {min_width=} {min_flex=}")
            # self._debug(f"  {child_width=} {width=} {remaining_width=}")

        if flex_total > 0:
            quantum = (remaining_width + min_flex) / flex_total
            # In an ideal flex layout, all flex children will have a width proportional
            # to their flex value. However, if a flex child has a flexible minimum width
            # constraint that is greater than the ideal width for a balanced flex
            # layout, they need to be removed from the flex calculation.
            # self._debug(f"PASS 1a; {quantum=}")
            for child in node.children:
                if child.style.flex and child.intrinsic.width is not None:
                    try:
                        ideal_width = quantum * child.style.flex
                        if child.intrinsic.width.value > ideal_width:
                            # self._debug(f"- {child} overflows ideal width")
                            flex_total -= child.style.flex
                            min_flex -= (
                                child.style.margin_left
                                + child.intrinsic.width.value
                                + child.style.margin_right
                            )
                    except AttributeError:
                        # Intrinsic width isn't flexible
                        pass

            if flex_total > 0:
                quantum = (remaining_width + min_flex) / flex_total
            else:
                quantum = 0
        else:
            quantum = 0
        # self._debug(f"END PASS 1; {min_width=} {width=} {min_flex=} {quantum=}")

        # Pass 2: Lay out children with an intrinsic flexible width,
        # or no width specification at all.
        for child in node.children:
            # self._debug(f"PASS 2 {child}")
            if child.style.width != NONE:
                # self._debug("- already laid out (explicit width)")
                pass
            elif child.style.flex:
                if child.intrinsic.width is not None:
                    try:
                        child_alloc_width = (
                            child.style.margin_left
                            + child.intrinsic.width.value
                            + child.style.margin_right
                        )
                        ideal_width = quantum * child.style.flex
                        # self._debug(f"- flexible intrinsic {child_alloc_width=}")
                        if ideal_width > child_alloc_width:
                            # self._debug(f"  {ideal_width=}")
                            child_alloc_width = ideal_width

                        child.style._layout_node(
                            child,
                            alloc_width=child_alloc_width,
                            alloc_height=available_height,
                            use_all_width=True,
                            use_all_height=child.style.direction == ROW,
                        )
                        # Our width calculation already takes into account the intrinsic
                        # width; that has now expanded as a result of layout, so adjust
                        # to use the new layout size. Min width may also change, by the
                        # same scheme, because the flex child can itself have children,
                        # and those grandchildren have now been laid out.
                        # self._debug(f"  sub {child.intrinsic.width.value=}")
                        # self._debug(f"  add {child.layout.content_width=}")
                        # self._debug(f"  add min {child.layout.min_content_width=}")
                        width = (
                            width
                            - child.intrinsic.width.value
                            + child.layout.content_width
                        )
                        min_width = (
                            min_width
                            - child.intrinsic.width.value
                            + child.layout.min_content_width
                        )
                    except AttributeError:
                        # self._debug("- already laid out (fixed intrinsic width)")
                        pass
                else:
                    if quantum:
                        # self._debug(f"- unspecified flex width with {quantum=}")
                        child_alloc_width = quantum * child.style.flex
                    else:
                        # self._debug("- unspecified flex width")
                        child_alloc_width = (
                            child.style.margin_left + child.style.margin_right
                        )

                    child.style._layout_node(
                        child,
                        alloc_width=child_alloc_width,
                        alloc_height=available_height,
                        use_all_width=True,
                        use_all_height=child.style.direction == ROW,
                    )
                    # We now know the final min_width/width that accounts for flexible
                    # sizing; add that to the overall.
                    # self._debug(f"  add {child.layout.min_content_width=}")
                    # self._debug(f"  add {child.layout.content_width=}")
                    width += child.layout.content_width
                    min_width += child.layout.min_content_width
            else:
                # self._debug("- already laid out (intrinsic non-flex width)")
                pass

            # self._debug(f"  {min_width=} {width=}")

        # self._debug(f"PASS 2 COMPLETE; USED {width=}")
        if use_all_width:
            width = max(width, available_width)
        # self._debug(f"COMPUTED {min_width=} {width=}")

        # Pass 3: Set the horizontal position of each child, and establish row height
        offset = 0
        height = 0
        min_height = 0
        for child in node.children:
            # self._debug(f"PASS 3: {child} AT HORIZONTAL {offset=}")
            if node.style.text_direction == RTL:
                # self._debug("- RTL")
                offset += child.layout.content_width + child.style.margin_right
                child.layout.content_left = width - offset
                offset += child.style.margin_left
            else:
                # self._debug("- LTR")
                offset += child.style.margin_left
                child.layout.content_left = offset
                offset += child.layout.content_width + child.style.margin_right

            child_height = (
                child.style.margin_top
                + child.layout.content_height
                + child.style.margin_bottom
            )
            height = max(height, child_height)

            min_child_height = (
                child.style.margin_top
                + child.layout.min_content_height
                + child.style.margin_bottom
            )
            min_height = max(min_height, min_child_height)

        # self._debug(f"ROW {min_height=} {height=}")
        if use_all_height:
            height = max(height, available_height)
        # self._debug(f"FINAL ROW {min_height=} {height=}")

        # Pass 4: set vertical position of each child.
        for child in node.children:
            # self._debug(f"PASS 4: {child}")
            extra = height - (
                child.layout.content_height
                + child.style.margin_top
                + child.style.margin_bottom
            )
            # self._debug(f"- row extra width {extra}")
            if self.align_items == END:
                child.layout.content_top = extra + child.style.margin_top
                # self._debug(f"  align {child} to bottom {child.layout.content_top=}")
            elif self.align_items == CENTER:
                child.layout.content_top = int(extra / 2) + child.style.margin_top
                # self._debug(f"  align {child} to center {child.layout.content_top=}")
            else:
                child.layout.content_top = child.style.margin_top
                # self._debug(f"  align {child} to top {child.layout.content_top=}")

        return min_width, width, min_height, height

    def _layout_column_children(
        self,
        node: Node,
        available_width: int,
        available_height: int,
        use_all_width: bool,
        use_all_height: bool,
    ) -> tuple[int, int, int, int]:
        # self._debug(f"LAYOUT COLUMN CHILDREN {available_width=} {available_height=}")
        # Pass 1: Lay out all children with a hard-specified height, or an
        # intrinsic non-flexible height. While iterating, collect the flex
        # total of remaining elements.
        flex_total = 0
        min_flex = 0
        height = 0
        min_height = 0
        remaining_height = available_height
        for child in node.children:
            # self._debug(f"PASS 1 {child}")
            if child.style.height != NONE:
                # self._debug(f"- fixed height {child.style.height}")
                child.style._layout_node(
                    child,
                    alloc_width=available_width,
                    alloc_height=remaining_height,
                    use_all_width=child.style.direction == COLUMN,
                    use_all_height=False,
                )
                child_content_height = child.layout.content_height
                # It doesn't matter how small the children can be laid out;
                # we have an intrinsic size; so don't use min_content_height
                min_child_content_height = child.layout.content_height
            elif child.intrinsic.height is not None:
                if hasattr(child.intrinsic.height, "value"):
                    if child.style.flex:
                        # self._debug(
                        #     f"- intrinsic flex height {child.intrinsic.height}"
                        # )
                        flex_total += child.style.flex
                        # Final child content size will be computed in pass 2, after the
                        # amount of flexible space is known. For now, set an initial
                        # content height based on the intrinsic size, which will be the
                        # minimum possible allocation.
                        child_content_height = child.intrinsic.height.value
                        min_child_content_height = child.intrinsic.height.value
                        min_flex += (
                            child.style.margin_top
                            + child_content_height
                            + child.style.margin_bottom
                        )
                    else:
                        # self._debug(f"- intrinsic non-flex {child.intrinsic.height=}")
                        child.style._layout_node(
                            child,
                            alloc_width=available_width,
                            alloc_height=0,
                            use_all_width=child.style.direction == COLUMN,
                            use_all_height=False,
                        )
                        child_content_height = child.layout.content_height
                        # It doesn't matter how small the children can be laid out;
                        # we have an intrinsic size; so don't use min_content_height
                        min_child_content_height = child.layout.content_height
                else:
                    # self._debug(f"- intrinsic {child.intrinsic.height=}")
                    child.style._layout_node(
                        child,
                        alloc_width=available_width,
                        alloc_height=remaining_height,
                        use_all_width=child.style.direction == COLUMN,
                        use_all_height=False,
                    )
                    child_content_height = child.layout.content_height
                    # It doesn't matter how small the children can be laid out;
                    # we have an intrinsic size; so don't use min_content_height
                    min_child_content_height = child.layout.content_height
            else:
                if child.style.flex:
                    # self._debug("- unspecified flex height")
                    flex_total += child.style.flex
                    # Final child content size will be computed in pass 2, after the
                    # amount of flexible space is known. For now, use 0 as the minimum,
                    # as that's the best hint the widget style can give.
                    child_content_height = 0
                    min_child_content_height = 0
                else:
                    # self._debug("- unspecified non-flex height")
                    child.style._layout_node(
                        child,
                        alloc_width=available_width,
                        alloc_height=remaining_height,
                        use_all_width=child.style.direction == COLUMN,
                        use_all_height=False,
                    )
                    child_content_height = child.layout.content_height
                    min_child_content_height = child.layout.min_content_height

            child_height = (
                child.style.margin_top
                + child_content_height
                + child.style.margin_bottom
            )
            height += child_height
            remaining_height -= child_height

            min_child_height = (
                child.style.margin_top
                + min_child_content_height
                + child.style.margin_bottom
            )
            min_height += min_child_height

            # self._debug(f"  {min_child_height=} {min_height=} {min_flex=}")
            # self._debug(f"  {child_height=} {height=} {remaining_height=}")

        if flex_total > 0:
            quantum = (remaining_height + min_flex) / flex_total
            # In an ideal flex layout, all flex children will have a height proportional
            # to their flex value. However, if a flex child has a flexible minimum
            # height constraint that is greater than the ideal height for a balanced
            # flex layout, they need to be removed from the flex calculation.
            # self._debug(f"PASS 1a; {quantum=}")
            for child in node.children:
                if child.style.flex and child.intrinsic.height is not None:
                    try:
                        ideal_height = quantum * child.style.flex
                        if child.intrinsic.height.value > ideal_height:
                            # self._debug(f"- {child} overflows ideal height")
                            flex_total -= child.style.flex
                            min_flex -= (
                                child.style.margin_top
                                + child.intrinsic.height.value
                                + child.style.margin_bottom
                            )
                    except AttributeError:
                        # Intrinsic height isn't flexible
                        pass

            if flex_total > 0:
                quantum = (min_flex + remaining_height) / flex_total
            else:
                quantum = 0
        else:
            quantum = 0

        # self._debug(f"END PASS 1; {min_height=} {height=} {min_flex=} {quantum=}")

        # Pass 2: Lay out children with an intrinsic flexible height,
        # or no height specification at all.
        for child in node.children:
            # self._debug(f"PASS 2 {child}")
            if child.style.height != NONE:
                # self._debug("- already laid out (explicit height)")
                pass
            elif child.style.flex:
                if child.intrinsic.height is not None:
                    try:
                        child_alloc_height = (
                            child.style.margin_top
                            + child.intrinsic.height.value
                            + child.style.margin_bottom
                        )
                        ideal_height = quantum * child.style.flex
                        # self._debug(f"- flexible intrinsic {child_alloc_height=}")
                        if ideal_height > child_alloc_height:
                            # self._debug(f"  {ideal_height=}")
                            child_alloc_height = ideal_height

                        child.style._layout_node(
                            child,
                            alloc_width=available_width,
                            alloc_height=child_alloc_height,
                            use_all_width=child.style.direction == COLUMN,
                            use_all_height=True,
                        )
                        # Our height calculation already takes into account the
                        # intrinsic height; that has now expanded as a result of layout,
                        # so adjust to use the new layout size. Min height may also
                        # change, by the same scheme, because the flex child can itself
                        # have children, and those grandchildren have now been laid out.
                        # self._debug(f"  sub {child.intrinsic.height.value=}")
                        # self._debug(f"  add {child.layout.content_height}")
                        # self._debug(f"  add min {child.layout.min_content_height}")
                        height = (
                            height
                            - child.intrinsic.height.value
                            + child.layout.content_height
                        )
                        min_height = (
                            min_height
                            - child.intrinsic.height.value
                            + child.layout.min_content_height
                        )
                    except AttributeError:
                        # self._debug("- already laid out (fixed intrinsic height)")
                        pass
                else:
                    if quantum:
                        # self._debug(f"- unspecified flex height with {quantum=}")
                        child_alloc_height = quantum * child.style.flex
                    else:
                        # self._debug("- unspecified flex height")
                        child_alloc_height = (
                            child.style.margin_top + child.style.margin_bottom
                        )

                    child.style._layout_node(
                        child,
                        alloc_width=available_width,
                        alloc_height=child_alloc_height,
                        use_all_width=child.style.direction == COLUMN,
                        use_all_height=True,
                    )
                    # We now know the final min_height/height that accounts for flexible
                    # sizing; add that to the overall.
                    # self._debug(f"  add {child.layout.min_content_height=}")
                    # self._debug(f"  add {child.layout.content_height=}")
                    height += child.layout.content_height
                    min_height += child.layout.min_content_height

            else:
                # self._debug("- already laid out (intrinsic non-flex height)")
                pass

            # self._debug(f"  {min_height=} {height=}")

        # self._debug(f"PASS 2 COMPLETE; USED {height=}")
        if use_all_height:
            height = max(height, available_height)
        # self._debug(f"COMPUTED {min_height=} {height=}")

        # Pass 3: Set the vertical position of each element, and establish column width
        offset = 0
        width = 0
        min_width = 0
        for child in node.children:
            # self._debug(f"PASS 3: {child} AT VERTICAL OFFSET {offset}")
            offset += child.style.margin_top
            child.layout.content_top = offset
            offset += child.layout.content_height + child.style.margin_bottom
            child_width = (
                child.layout.content_width
                + child.style.margin_left
                + child.style.margin_right
            )
            width = max(width, child_width)

            min_child_width = (
                child.style.margin_left
                + child.layout.min_content_width
                + child.style.margin_right
            )
            min_width = max(min_width, min_child_width)

        # self._debug(f"ROW {min_width=} {width=}")
        if use_all_width:
            width = max(width, available_width)
        # self._debug(f"FINAL ROW {min_width=} {width=}")

        # Pass 4: set horizontal position of each child.
        for child in node.children:
            # self._debug(f"PASS 4: {child}")
            extra = width - (
                child.layout.content_width
                + child.style.margin_left
                + child.style.margin_right
            )
            # self._debug(f"-  row extra width {extra}")
            if (self.text_direction, self.align_items) in [(LTR, END), (RTL, START)]:
                child.layout.content_left = extra + child.style.margin_left
                # self._debug(f"  align {child} to right {child.layout.content_left=}")
            elif self.align_items == CENTER:
                child.layout.content_left = int(extra / 2) + child.style.margin_left
                # self._debug(f"  align {child} to center {child.layout.content_left=}")
            else:
                child.layout.content_left = child.style.margin_left
                # self._debug(f"  align {child} to left {child.layout.content_left=}")

        return min_width, width, min_height, height

    def __css__(self) -> str:
        css = []
        # display
        if self.display == NONE:
            css.append("display: none;")
        else:
            # if self.display != NONE, it must be pack; it will inherit
            # the pack definition from the Toga stylesheet.
            pass

        # visibility
        if self.visibility != VISIBLE:
            css.append(f"visibility: {self.visibility};")

        # direction
        css.append(f"flex-direction: {self.direction.lower()};")
        # flex
        if (self.width == NONE and self.direction == ROW) or (
            self.height == NONE and self.direction == COLUMN
        ):
            css.append(f"flex: {self.flex} 0 auto;")

        # width/flex
        if self.width != NONE:
            css.append(f"width: {self.width}px;")

        # height/flex
        if self.height != NONE:
            css.append(f"height: {self.height}px;")

        # align_items
        if self.align_items:
            css.append(f"align-items: {self.align_items};")

        # margin_*
        if self.margin_top:
            css.append(f"margin-top: {self.margin_top}px;")
        if self.margin_bottom:
            css.append(f"margin-bottom: {self.margin_bottom}px;")
        if self.margin_left:
            css.append(f"margin-left: {self.margin_left}px;")
        if self.margin_right:
            css.append(f"margin-right: {self.margin_right}px;")

        # color
        if self.color:
            css.append(f"color: {self.color};")

        # background_color
        if self.background_color:
            css.append(f"background-color: {self.background_color};")

        # text_align
        if self.text_align:
            css.append(f"text-align: {self.text_align};")

        # text_direction
        if self.text_direction != LTR:
            css.append(f"text-direction: {self.text_direction};")

        # font-*
        if self.font_family != SYSTEM:
            if " " in self.font_family:
                css.append(f'font-family: "{self.font_family}";')
            else:
                css.append(f"font-family: {self.font_family};")
        if self.font_size != SYSTEM_DEFAULT_FONT_SIZE:
            css.append(f"font-size: {self.font_size}pt;")
        if self.font_weight != NORMAL:
            css.append(f"font-weight: {self.font_weight};")
        if self.font_style != NORMAL:
            css.append(f"font-style: {self.font_style};")
        if self.font_variant != NORMAL:
            css.append(f"font-variant: {self.font_variant};")

        return " ".join(css)


Pack.validated_property("display", choices=DISPLAY_CHOICES, initial=PACK)
Pack.validated_property("visibility", choices=VISIBILITY_CHOICES, initial=VISIBLE)
Pack.validated_property("direction", choices=DIRECTION_CHOICES, initial=ROW)
Pack.validated_property("align_items", choices=ALIGN_ITEMS_CHOICES)
# Deprecated, but maintained for backwards compatibility with Toga <= 0.4.8
Pack.validated_property("alignment", choices=ALIGNMENT_CHOICES)

Pack.validated_property("width", choices=SIZE_CHOICES, initial=NONE)
Pack.validated_property("height", choices=SIZE_CHOICES, initial=NONE)
Pack.validated_property("flex", choices=FLEX_CHOICES, initial=0)

Pack.validated_property("margin_top", choices=MARGIN_CHOICES, initial=0)
Pack.validated_property("margin_right", choices=MARGIN_CHOICES, initial=0)
Pack.validated_property("margin_bottom", choices=MARGIN_CHOICES, initial=0)
Pack.validated_property("margin_left", choices=MARGIN_CHOICES, initial=0)
Pack.directional_property("margin%s")

Pack.validated_property("color", choices=COLOR_CHOICES)
Pack.validated_property("background_color", choices=BACKGROUND_COLOR_CHOICES)

Pack.validated_property("text_align", choices=TEXT_ALIGN_CHOICES)
Pack.validated_property("text_direction", choices=TEXT_DIRECTION_CHOICES, initial=LTR)

Pack.validated_property("font_family", choices=FONT_FAMILY_CHOICES, initial=SYSTEM)
# Pack.list_property('font_family', choices=FONT_FAMILY_CHOICES)
Pack.validated_property("font_style", choices=FONT_STYLE_CHOICES, initial=NORMAL)
Pack.validated_property("font_variant", choices=FONT_VARIANT_CHOICES, initial=NORMAL)
Pack.validated_property("font_weight", choices=FONT_WEIGHT_CHOICES, initial=NORMAL)
Pack.validated_property(
    "font_size", choices=FONT_SIZE_CHOICES, initial=SYSTEM_DEFAULT_FONT_SIZE
)
# Pack.composite_property([
#     'font_family', 'font_style', 'font_variant', 'font_weight', 'font_size'
#     FONT_CHOICES
# ])
