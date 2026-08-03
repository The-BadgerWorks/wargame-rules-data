# AI-Assisted: Claude Code (model: claude-opus-5) - Validate stage package (tasks T066-T068).
"""The ``validate`` stage: the checklist in data-model.md §8, one module per concern.

Two rules run through all of it. **Severity is a property of the code**, fixed in the finding
catalogue — a run may not decide that a normally-blocking finding is advisory today. And **any
unresolved blocking finding refuses publication**, with no override flag: the only way past one
is to fix the data or record a dated resolution (FR-029, ``validation-report.md`` §1).
"""
