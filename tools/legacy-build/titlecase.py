"""Title Case for headings, subheadings, labels and standalone keywords.

Explanatory prose stays in sentence case: empty-state descriptions, settings
notes, toggle sub-lines, import-mode sub-lines, the RIR/RPE popover body and
scale, crop hints, status lines and placeholders. Values stay as they are
(units, 'not set', '2 exercises'), because title-casing a value reads as a
label and makes the pairing ambiguous.

Title Case here follows the usual convention: articles, coordinating
conjunctions and short prepositions stay lowercase unless they lead or close
the phrase - 'Start a Workout', 'Save These Values for Next Time',
'Update the Whole Template'.
"""

PAIRS = [
    # ---------------------------------------------------------- page headings
    ("'Good morning'", "'Good Morning'"),
    ("'Good afternoon'", "'Good Afternoon'"),
    ("'Good evening'", "'Good Evening'"),
    ("'Still up'", "'Still Up'"),
    ('<div class="cta-title">Start a workout</div>', '<div class="cta-title">Start a Workout</div>'),
    ('<div class="cta-eyebrow">Roo is warmed up</div>', '<div class="cta-eyebrow">Roo Is Warmed Up</div>'),
    ('<div class="cta-eyebrow">Session running</div>', '<div class="cta-eyebrow">Session Running</div>'),

    # ------------------------------------------------------------ stat labels
    ('<div class="stat-lbl">day streak</div>', '<div class="stat-lbl">Day Streak</div>'),
    ('<div class="stat-lbl">this month</div>', '<div class="stat-lbl">This Month</div>'),
    ('<div class="stat-lbl">all time</div>', '<div class="stat-lbl">All Time</div>'),
    ('<div class="stat-lbl">workouts</div>', '<div class="stat-lbl">Workouts</div>'),
    ('<div class="stat-lbl">exercises</div>', '<div class="stat-lbl">Exercises</div>'),

    # --------------------------------------------------------- section titles
    ('<div class="section-title"><span>Your training</span>', '<div class="section-title"><span>Your Training</span>'),

    # ---------------------------------------------------------------- profile
    ("'Your profile')+'</div>'", "'Your Profile')+'</div>'"),
    ("'Add picture'", "'Add Picture'"),
    ('<h2>Adjust picture</h2>', '<h2>Adjust Picture</h2>'),
    ('>Use photo<', '>Use Photo<'),

    # --------------------------------------------------------- field labels
    ('<label class="field-label">Tracking fields</label>', '<label class="field-label">Tracking Fields</label>'),
    ('<label class="field-label">Default rest (seconds) ', '<label class="field-label">Default Rest (Seconds) '),
    ('<div class="field-label">Default rest</div>', '<div class="field-label">Default Rest</div>'),
    ('<span class="field-optional">optional</span>', '<span class="field-optional">Optional</span>'),

    # ---------------------------------------------------- exercise field types
    ("+' Time (target)</button>'", "+' Time (Target)</button>'"),
    ("+' Time (measured)</button>'", "+' Time (Measured)</button>'"),
    ('>Add field</button>', '>Add Field</button>'),
    ('<div class="ex-card-name">Deleted exercise</div>', '<div class="ex-card-name">Deleted Exercise</div>'),

    # -------------------------------------------------------------- workout
    ('Default rest: ', 'Default Rest: '),
    ('<p>Select an exercise</p>', '<p>Select an Exercise</p>'),
    ('>View full history ', '>View Full History '),

    # ----------------------------------------------------------- rest timer
    ("'Rest complete'", "'Rest Complete'"),

    # ------------------------------------------------------- finish workout
    ('<h2>Finish workout</h2>', '<h2>Finish Workout</h2>'),
    ("'Save these values for next time'", "'Save These Values for Next Time'"),
    ("'Update the whole template'", "'Update the Whole Template'"),
    ("'Update target times in &ldquo;'", "'Update Target Times in &ldquo;'"),

    # -------------------------------------------------------------- settings
    ('<span>Weight unit</span>', '<span>Weight Unit</span>'),
    (" Settings &amp; backup</button>", " Settings &amp; Backup</button>"),
    ('<div class="settings-section-label">Danger zone</div>', '<div class="settings-section-label">Danger Zone</div>'),
    ('<span>Export data file</span>', '<span>Export Data File</span>'),
    ('<span>Export portable copy</span>', '<span>Export Portable Copy</span>'),
    ('<span>Import backup</span>', '<span>Import Backup</span>'),
    ('<span>Reset all data</span>', '<span>Reset All Data</span>'),

    # ----------------------------------------------------------- backup flow
    ('<strong>Back up your data</strong>', '<strong>Back Up Your Data</strong>'),
    ('>Export now</button>', '>Export Now</button>'),
    ('<h2>Backup file opened</h2>', '<h2>Backup File Opened</h2>'),
    ('Backup loaded &mdash; choose how to apply it', 'Backup Loaded &mdash; Choose How to Apply It'),
    ('<span>Backup date</span>', '<span>Backup Date</span>'),
    ('<span class="import-mode-title">Replace everything</span>', '<span class="import-mode-title">Replace Everything</span>'),
    ('<span>In this browser</span>', '<span>In This Browser</span>'),
    ('<span>In this file</span>', '<span>In This File</span>'),
    ('>Keep current</button>', '>Keep Current</button>'),
    ('>Load backup</button>', '>Load Backup</button>'),
    ('>Export current first</button>', '>Export Current First</button>'),
    ('<span>From file</span>', '<span>From File</span>'),
    ('<span>Right now</span>', '<span>Right Now</span>'),
]


def apply(src):
    missed = []
    for old, new in PAIRS:
        n = src.count(old)
        if n == 0:
            missed.append(old)
            continue
        src = src.replace(old, new)
    assert not missed, "title-case strings not found:\n  " + "\n  ".join(repr(m) for m in missed)
    return src
