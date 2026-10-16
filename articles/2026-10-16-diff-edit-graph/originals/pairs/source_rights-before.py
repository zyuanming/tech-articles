"""Conservative asset permissions: public visibility is not a reuse grant."""
from __future__ import annotations

import re
import hashlib
from pathlib import Path

RIGHTS_STATUSES = {"AUTO_REUSE_ALLOWED", "ATTRIBUTION_REQUIRED", "HUMAN_REVIEW_REQUIRED", "NO_REUSE"}
CC0 = "https://creativecommons.org/publicdomain/zero/1.0/"
CC_BY = "https://creativecommons.org/licenses/by/4.0/"
# A person's likeness is not a technical figure. The publisher's standing
# approval covers screenshots, diagrams and paper figures from the source
# page; a portrait or headshot pulled off the same page is a different
# thing and stays with the human.
PEOPLE_RE = re.compile(
    r"/(?:team|people|staff|authors?|avatar|avatars|headshot|portraits?|bios?|about)"
    r"(?:/|[-_.])", re.I)


def is_people_asset(asset: dict) -> bool:
    return bool(PEOPLE_RE.search(str(asset.get("asset_url") or "")))


TYPE_LABELS = {
    "screenshot": "截图", "page_region_screenshot": "原文区域截图",
    "paper_figure": "论文插图", "source_table": "原表", "diagram": "示意图",
    "chart": "图表", "photo": "照片", "table": "表格", "comparison": "对比图",
    "timeline": "时间线", "code_card": "代码", "concept_card": "概念图",
}

_POLICY: list[str] = []


def unknown_license_policy() -> str:
    """The publisher's standing decision on unlicensed source-page figures.

    Defaults to human review. `attribution_allowed` is set in
    config/visual_style.yaml once the publisher has accepted reusing such
    figures with a credit.
    """
    if not _POLICY:
        try:
            from .style import load_style
            _POLICY.append(str(load_style().get("source_discovery", {})
                               .get("unknown_license_policy", "human_review")))
        except Exception:  # a config problem must not silently grant reuse
            _POLICY.append("human_review")
    return _POLICY[0]


def evaluate_rights(asset: dict, unknown_license_policy: str = "human_review") -> dict:
    """Decide reuse permission. `unknown_license_policy` is the publisher's call.

    "attribution_allowed" means the publisher has accepted reusing unlicensed
    source-page figures with a credit, which is ordinary practice in technical
    media but is not a licence. It never overrides an explicit prohibition, and
    it never covers a person's likeness.
    """
    result = {"rights_status": "HUMAN_REVIEW_REQUIRED", "auto_reuse_allowed": False,
              "attribution_required": True, "adaptation_allowed": None,
              "commercial_reuse_allowed": None, "rights_reason": "没有明确的资产复用许可"}
    license_text = str(asset.get("license") or "").upper().strip()
    if asset.get("reuse_prohibited") is True or re.search(r"ALL RIGHTS RESERVED|NO REUSE|禁止转载|不得转载", license_text):
        return {**result, "rights_status": "NO_REUSE", "rights_reason": "来源明确禁止复用"}
    if (unknown_license_policy == "attribution_allowed" and not is_people_asset(asset)
            and not license_text):
        # No stated licence at all: the publisher has approved reuse with a
        # credit. An explicit licence that simply fails the checks below still
        # falls through to human review rather than being waved past.
        return {**result, "rights_status": "ATTRIBUTION_REQUIRED",
                "auto_reuse_allowed": True, "adaptation_allowed": False,
                "commercial_reuse_allowed": False,
                "rights_reason": "无明示许可；发布方已批准署名使用来源图（人物肖像除外）"}
    # Repository code licenses do not silently authorize screenshots or third-party figures.
    if asset.get("license_scope") not in {"asset", "all_assets"} or not asset.get("rights_evidence"):
        return result
    url = str(asset.get("license_url") or "").rstrip("/")
    if license_text == "MIT":
        # Require reviewed asset scope, not merely a repository's code license.
        # The retained notice is also rendered in the accompanying caption.
        ready = bool(url.startswith("https://") and asset.get("creator")
                     and asset.get("source_url") and asset.get("caption")
                     and asset.get("copyright_notice") and asset.get("license_notice")
                     and asset.get("asset_license_review") == "documentation_scope_reviewed")
        return {**result, "rights_status": "ATTRIBUTION_REQUIRED" if ready else "HUMAN_REVIEW_REQUIRED",
                "auto_reuse_allowed": ready, "adaptation_allowed": True if ready else None,
                "commercial_reuse_allowed": True if ready else None,
                "rights_reason": "已核对文档素材范围，保留 MIT 版权与许可声明" if ready else "MIT 素材范围或许可声明尚未完整核对"}
    if license_text in {"CC0", "CC0-1.0"} and url == CC0.rstrip("/"):
        return {**result, "rights_status": "AUTO_REUSE_ALLOWED", "auto_reuse_allowed": True,
                "attribution_required": False, "adaptation_allowed": True,
                "commercial_reuse_allowed": True, "rights_reason": "明确资产范围的 CC0 许可"}
    if license_text in {"CC-BY-4.0", "CC BY 4.0"} and url == CC_BY.rstrip("/"):
        ready = bool(asset.get("creator") and asset.get("source_url") and asset.get("caption"))
        return {**result, "rights_status": "ATTRIBUTION_REQUIRED" if ready else "HUMAN_REVIEW_REQUIRED",
                "auto_reuse_allowed": ready, "adaptation_allowed": True,
                "commercial_reuse_allowed": True,
                "rights_reason": "CC BY 署名与许可链接齐全" if ready else "CC BY 署名信息不完整"}
    return result


def attribution_caption(asset: dict, adapted: bool = False) -> str:
    label = (asset.get("figure_number")
             or TYPE_LABELS.get(str(asset.get("type") or ""), "图"))
    title = str(asset.get("source_title") or "").strip()
    head = f"图：{title}，{label}。" if title else f"图：{label}。"
    parts = [head, asset.get("caption", "")]
    if asset.get("creator"):
        parts.append("作者：" + str(asset["creator"]) + "。")
    if asset.get("source_url"):
        parts.append(f"[来源]({asset['source_url']})")
    if asset.get("license_url"):
        parts.append(f"[{asset.get('license') or '许可'}]({asset['license_url']})")
    if asset.get("copyright_notice"):
        parts.append(str(asset["copyright_notice"]))
    if asset.get("license_notice"):
        parts.append(str(asset["license_notice"]))
    if adapted:
        parts.append("根据原图／原数据整理；已作手机排版调整。")
    return " ".join(p for p in parts if p)


def source_caption(asset: dict) -> str:
    """The figure's own caption, for when the credit lives in the endnotes.

    The publisher's standing decision (2026-10-07) is that source images carry
    a single credit at the foot of the article, so the caption under the figure
    is free to describe the figure instead of repeating who owns it.
    """
    return str(asset.get('caption') or asset.get('source_title') or '').strip()


def source_endnotes(figures: dict) -> list[str]:
    """Source credits, one short line per source, separate from captions.

    These render as small print at the foot of the article, so they carry the
    credit and the pointer to the licence, not the licence text itself: pasting
    the whole MIT body (or one line per reused asset from the same source) made
    the footer longer than the article it credits.
    """
    notes, seen = [], set()
    for visual in figures.values():
        if visual.get('attribution_placement') != 'endnotes':
            continue
        asset = visual.get('source_asset', {})
        creator = str(asset.get('creator') or '').strip()
        source_url = str(asset.get('source_url') or '').strip()
        key = (creator, source_url)
        if key in seen:
            continue
        seen.add(key)
        # Name the source, not just the host: 署名 without a name says nothing.
        label = creator or str(asset.get('source_title') or '').strip()
        parts = [f"素材：{label}" if label else "素材"]
        if source_url:
            parts.append(source_url)
        licence = str(asset.get('license') or '').strip()
        licence_url = str(asset.get('license_url') or '').strip()
        if licence or licence_url:
            parts.append(f"{licence} {licence_url}".strip())
        # The permission notice is what an MIT-style credit legally has to
        # carry, so it stays; it is collapsed to one line rather than dropped,
        # because the whole notice verbatim is what made the footer longer
        # than the article it credits.
        for field in ('copyright_notice', 'license_notice'):
            if asset.get(field):
                parts.append(" ".join(str(asset[field]).split()))
        notes.append("；".join(p for p in parts if p))
    return notes


def validate_source_visuals(manifest: dict, out_dir: Path, *, local_preview=False,
                            rendered_html=None) -> list[str]:
    errors = []
    for visual in manifest.get("visuals", []):
        if visual.get("status") != "ready" or visual.get("visual_source") not in {"source_original", "source_evidence"}:
            continue
        asset = visual.get("source_asset", {})
        # Same policy as discovery: a manifest built under the publisher's
        # attribution decision must not be rejected here for the very status
        # that decision produces.
        rights = evaluate_rights(asset, unknown_license_policy())
        path = (out_dir / visual.get("output", "")).resolve()
        preview_exception = (local_preview and visual.get('preview_only') is True
                             and rights['rights_status'] == 'HUMAN_REVIEW_REQUIRED')
        if not rights["auto_reuse_allowed"] and not preview_exception:
            errors.append(visual["id"] + ": SOURCE_VISUAL_RIGHTS_FAILED")
        endnotes = visual.get('attribution_placement') == 'endnotes'
        expected_caption = source_caption(asset) if endnotes else attribution_caption(asset)
        if visual.get("caption") != expected_caption:
            errors.append(visual["id"] + ": SOURCE_ATTRIBUTION_FAILED")
        if (not path.is_relative_to(out_dir.resolve()) or not path.is_file() or
                hashlib.sha256(path.read_bytes()).hexdigest() != asset.get("asset_sha256")):
            errors.append(visual["id"] + ": SOURCE_ASSET_INTEGRITY_FAILED")
    if rendered_html is not None:
        import html
        from html.parser import HTMLParser
        class Text(HTMLParser):
            def __init__(self):
                super().__init__(); self.parts = []
            def handle_data(self, value):
                self.parts.append(value)
        parser = Text(); parser.feed(rendered_html)
        visible = ' '.join(' '.join(parser.parts).split())
        for note in source_endnotes({v['id']: v for v in manifest.get('visuals', [])}):
            if ' '.join(html.unescape(note).split()) not in visible:
                errors.append('SOURCE_ENDNOTES_MISSING')
    return errors
