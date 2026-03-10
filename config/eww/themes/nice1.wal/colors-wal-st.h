const char *colorname[] = {

  /* 8 normal colors */
  [0] = "#0d0f12", /* black   */
  [1] = "#5A5D62", /* red     */
  [2] = "#5E6166", /* green   */
  [3] = "#6E7176", /* yellow  */
  [4] = "#7A7D82", /* blue    */
  [5] = "#7E8186", /* magenta */
  [6] = "#888B90", /* cyan    */
  [7] = "#c4c5c8", /* white   */

  /* 8 bright colors */
  [8]  = "#89898c",  /* black   */
  [9]  = "#5A5D62",  /* red     */
  [10] = "#5E6166", /* green   */
  [11] = "#6E7176", /* yellow  */
  [12] = "#7A7D82", /* blue    */
  [13] = "#7E8186", /* magenta */
  [14] = "#888B90", /* cyan    */
  [15] = "#c4c5c8", /* white   */

  /* special colors */
  [256] = "#0d0f12", /* background */
  [257] = "#c4c5c8", /* foreground */
  [258] = "#c4c5c8",     /* cursor */
};

/* Default colors (colorname index)
 * foreground, background, cursor */
 unsigned int defaultbg = 0;
 unsigned int defaultfg = 257;
 unsigned int defaultcs = 258;
 unsigned int defaultrcs= 258;
