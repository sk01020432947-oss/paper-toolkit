---
category: literature-note
citekey: "{{citekey}}"
title: "{{title | replace('"', '')}}"
year: {% if date %}{{date | format("YYYY")}}{% endif %}
tags: [문헌노트{% for t in tags %}, "{{t.tag}}"{% endfor %}]
---

# {{title}}

> [!cite]+ 서지 (APA)
> {{bibliography}}

**저자**:: {% for creator in creators %}{{creator.firstName}} {{creator.lastName}}{% if not loop.last %}, {% endif %}{% endfor %}
**연도**:: {% if date %}{{date | format("YYYY")}}{% endif %}
**링크**:: [Zotero에서 열기]({{desktopURI}}){% if DOI %} · [DOI](https://doi.org/{{DOI}}){% endif %}{% if url %} · [원문]({{url}}){% endif %}

{% if markdownNotes %}
## 논문 메모 (Item Notes)

{{markdownNotes}}
{% endif %}

## Annotations

%% 아래 persist 블록: 재가져오기 시 기존 내용은 유지되고 새 하이라이트만 추가됩니다 %%
{% persist "annotations" %}
{% set annots = annotations | filterby("date", "dateafter", lastImportDate) %}
{% if annots.length > 0 %}
### 📥 {{importDate | format("YYYY-MM-DD HH:mm")}} 가져옴

{% for annot in annots %}
{%- if annot.imageRelativePath %}
![[{{annot.imageRelativePath}}]]
{%- endif %}
{%- if annot.annotatedText %}
> <mark class="hltr-{{annot.colorCategory | lower}}">{{annot.annotatedText | nl2br}}</mark> — [p. {{annot.pageLabel}}]({{annot.desktopURI}})
{%- endif %}
{%- if annot.comment %}
> 💬 {{annot.comment | nl2br}}
{%- endif %}

{% endfor %}
{% endif %}
{% endpersist %}
