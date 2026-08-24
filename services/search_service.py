from dataclasses import dataclass
from typing import List, Optional
from services.settings_index import SettingsIndex, SearchItem
from localization import i18n, t

@dataclass
class SearchResult:
    item: SearchItem
    score: float
    display_title: str
    display_section: str
    display_page: str
    matched_reason: str = ""

    @property
    def id(self) -> str:
        return self.item.id

    @property
    def page(self) -> str:
        return self.item.page

    @property
    def section(self) -> str:
        return self.item.section

    @property
    def title(self) -> str:
        return self.item.title

    @property
    def icon_color(self) -> str:
        return self.item.icon_color


class SearchService:
    def __init__(self):
        self._index = SettingsIndex.get_instance()

    def search(self, query: str, lang: Optional[str] = None) -> List[SearchResult]:
        """
        Performs fast, multi-attribute, scored search across all indexed settings.
        Zero I/O and zero D-Bus queries. Returns sorted results by relevance.
        """
        raw_q = query.strip()
        if not raw_q:
            return []

        q = raw_q.lower()
        q_tokens = [tok for tok in q.replace("-", " ").replace("_", " ").split() if tok]
        if not q_tokens:
            return []

        results: List[SearchResult] = []
        all_items = self._index.get_all_items()

        for item in all_items:
            # Resolve localized title, section and page
            loc_title = t(item.title_key, item.title) if item.title_key else item.title
            loc_section = t(item.section_key, item.section) if item.section_key else item.section
            loc_page = t(f"nav.{item.page.lower().replace(' ', '_').replace('-', '_').replace('&', '')}", item.page)

            # Clean uppercase strings for result display
            if loc_title.isupper() and len(loc_title) > 3:
                loc_title = loc_title.capitalize()
            if loc_section.isupper() and len(loc_section) > 3:
                loc_section = loc_section.capitalize()

            score = 0.0
            matched_reasons = []

            title_lower = item.title.lower()
            loc_title_lower = loc_title.lower()
            section_lower = item.section.lower()
            loc_section_lower = loc_section.lower()
            page_lower = item.page.lower()
            loc_page_lower = loc_page.lower()
            desc_lower = item.description.lower()

            # 1. Exact Title Match
            if q == title_lower or q == loc_title_lower:
                score += 160.0
                matched_reasons.append("exact_title")
            elif title_lower.startswith(q) or loc_title_lower.startswith(q):
                score += 110.0
                matched_reasons.append("title_prefix")
            elif f" {q} " in f" {title_lower} " or f" {q} " in f" {loc_title_lower} ":
                score += 85.0
                matched_reasons.append("title_word")
            elif q in title_lower or q in loc_title_lower:
                score += 65.0
                matched_reasons.append("title_substr")

            # 2. Aliases & Synonyms (Highest priority for natural queries e.g. "dark mode", "wifi", "mouse speed")
            alias_matched = False
            for alias in item.aliases:
                al_lower = alias.lower()
                if q == al_lower:
                    score += 130.0
                    alias_matched = True
                    matched_reasons.append(f"exact_alias({alias})")
                    break
                elif al_lower.startswith(q):
                    score += 90.0
                    alias_matched = True
                    matched_reasons.append(f"alias_prefix({alias})")
                    break
                elif q in al_lower or al_lower in q:
                    score += 70.0
                    alias_matched = True
                    matched_reasons.append(f"alias_substr({alias})")
                    break

            # 3. Keywords Match
            kw_matched = False
            for kw in item.keywords:
                kw_lower = kw.lower()
                if q == kw_lower:
                    score += 80.0
                    kw_matched = True
                    matched_reasons.append(f"exact_kw({kw})")
                    break
                elif kw_lower.startswith(q):
                    score += 60.0
                    kw_matched = True
                    matched_reasons.append(f"kw_prefix({kw})")
                    break
                elif q in kw_lower:
                    score += 45.0
                    kw_matched = True
                    matched_reasons.append(f"kw_substr({kw})")
                    break

            # 4. Section Match
            if q == section_lower or q == loc_section_lower:
                score += 75.0
                matched_reasons.append("exact_section")
            elif section_lower.startswith(q) or loc_section_lower.startswith(q):
                score += 55.0
                matched_reasons.append("section_prefix")
            elif q in section_lower or q in loc_section_lower:
                score += 40.0
                matched_reasons.append("section_substr")

            # 5. Page Name Match
            if q == page_lower or q == loc_page_lower:
                score += 50.0
                matched_reasons.append("exact_page")
            elif page_lower.startswith(q) or loc_page_lower.startswith(q):
                score += 40.0
                matched_reasons.append("page_prefix")
            elif q in page_lower or q in loc_page_lower:
                score += 30.0
                matched_reasons.append("page_substr")

            # 6. Description Match
            if q in desc_lower:
                score += 25.0
                matched_reasons.append("description")

            # 7. Multi-word token coverage check
            if len(q_tokens) > 1:
                token_matches = 0
                all_text = f"{title_lower} {loc_title_lower} {section_lower} {loc_section_lower} {page_lower} {loc_page_lower} {' '.join(item.aliases).lower()} {' '.join(item.keywords).lower()} {desc_lower}"
                for tok in q_tokens:
                    if tok in all_text:
                        token_matches += 1

                if token_matches == len(q_tokens):
                    score += 45.0 * (token_matches / len(q_tokens))
                    matched_reasons.append("all_tokens_matched")
                elif token_matches > 0:
                    score += 15.0 * (token_matches / len(q_tokens))

            if score >= 20.0:
                results.append(
                    SearchResult(
                        item=item,
                        score=score,
                        display_title=loc_title,
                        display_section=loc_section,
                        display_page=loc_page,
                        matched_reason=", ".join(matched_reasons),
                    )
                )

        # Sort results strictly by relevance score descending
        results.sort(key=lambda r: r.score, reverse=True)
        return results
