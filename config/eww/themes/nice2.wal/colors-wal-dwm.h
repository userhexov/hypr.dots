static const char norm_fg[] = "#c4c5c8";
static const char norm_bg[] = "#0d0f12";
static const char norm_border[] = "#89898c";

static const char sel_fg[] = "#c4c5c8";
static const char sel_bg[] = "#5E6166";
static const char sel_border[] = "#c4c5c8";

static const char urg_fg[] = "#c4c5c8";
static const char urg_bg[] = "#5A5D62";
static const char urg_border[] = "#5A5D62";

static const char *colors[][3]      = {
    /*               fg           bg         border                         */
    [SchemeNorm] = { norm_fg,     norm_bg,   norm_border }, // unfocused wins
    [SchemeSel]  = { sel_fg,      sel_bg,    sel_border },  // the focused win
    [SchemeUrg] =  { urg_fg,      urg_bg,    urg_border },
};
