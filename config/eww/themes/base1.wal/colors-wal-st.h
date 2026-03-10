const char *colorname[] = {

  /* 8 normal colors */
  [0] = "#050506", /* black   */
  [1] = "#7F8082", /* red     */
  [2] = "#919193", /* green   */
  [3] = "#9E9FA1", /* yellow  */
  [4] = "#B1B1B2", /* blue    */
  [5] = "#BEC0C0", /* magenta */
  [6] = "#D0D0D0", /* cyan    */
  [7] = "#e7e7e6", /* white   */

  /* 8 bright colors */
  [8]  = "#a1a1a1",  /* black   */
  [9]  = "#7F8082",  /* red     */
  [10] = "#919193", /* green   */
  [11] = "#9E9FA1", /* yellow  */
  [12] = "#B1B1B2", /* blue    */
  [13] = "#BEC0C0", /* magenta */
  [14] = "#D0D0D0", /* cyan    */
  [15] = "#e7e7e6", /* white   */

  /* special colors */
  [256] = "#050506", /* background */
  [257] = "#e7e7e6", /* foreground */
  [258] = "#e7e7e6",     /* cursor */
};

/* Default colors (colorname index)
 * foreground, background, cursor */
 unsigned int defaultbg = 0;
 unsigned int defaultfg = 257;
 unsigned int defaultcs = 258;
 unsigned int defaultrcs= 258;
