# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2026 Rizonesoft
"""The Word baseline ids the inventory documents as absent, and why (design/inventory/REFERENCE.md). The capture (scripts/capture-ui.py) refuses an absence that is captured after all, and the coverage report (scripts/inventory-report.py) counts them as documented absent rather than unmatched."""
import word_backstage

# The baseline tab rows Word does not show in a normal .docx session (REFERENCE.md, Word ribbon reconciliation).
WORD_RECONCILED_ABSENT_TABS = {
    "TabAddIns": "legacy CommandBar add-in container tab; hidden when no legacy add-in registers custom CommandBar controls",
    "TabSyntex": "SharePoint Syntex enterprise content assembly tab; requires a Microsoft Syntex tenant service license",
    "TabBlogPost": "legacy Weblog post editing tab; only loaded when Word starts in the deprecated Blog Post template mode",
    "TabBlogInsert": "legacy Weblog insert tab; only loaded when Word starts in the deprecated Blog Post template mode",
    "TabConflicts": "co-authoring server merge conflict resolution mode tab; only shown during an active sync conflict",
    "TabBroadcastPresentation": "retired Office Presentation Service broadcast mode tab",
    "TabChartToolsDesign": "legacy Office 2007-2010 chart contextual tab superseded by TabChartToolsDesignNew",
    "TabChartToolsLayout": "legacy Office 2007-2010 chart layout tab superseded by TabChartToolsDesignNew and TabChartToolsFormatNew",
    "TabChartToolsFormat": "legacy Office 2007-2010 chart format tab superseded by TabChartToolsFormatNew",
    "TabDrawingToolsFormatClassic": "legacy VML drawing/AutoShape tab superseded by DrawingML TabDrawingToolsFormat",
    "TabPictureToolsFormatClassic": "legacy VML picture tab superseded by DrawingML TabPictureToolsFormat",
    "TabTextBoxToolsFormat": "legacy VML text box tab superseded by DrawingML TabDrawingToolsFormat",
    "TabWordArtToolsFormat": "legacy VML WordArt tab superseded by DrawingML TabDrawingToolsFormat",
    "TabDiagramToolsFormatClassic": "legacy Office 2003 diagram tab superseded by SmartArt TabSmartArtToolsDesign and TabSmartArtToolsFormat",
    "TabOrganizationChartToolsFormat": "legacy Office 2003 organization chart tab superseded by SmartArt TabSmartArtToolsDesign and TabSmartArtToolsFormat",
    "TabInkToolsPens": "legacy contextual Ink Tools Pens tab superseded by the always-available Draw TabDrawInk tab",
}


def documented(app):
    """Every baseline idMso of `app` the inventory documents as absent, with its reason."""
    if app != "word":
        return {}
    return {**WORD_RECONCILED_ABSENT_TABS, **word_backstage.ABSENT}
