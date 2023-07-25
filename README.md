# Curriculum Vitae

CV generator utilizing a combination of Emacs Org-Mode, Python and JSON data. Works well for me and can easily be auto generated. I always have the newest versions as releases on Github, though I have redacted some information for privacy.

## Overview of build process
```mermaid
graph LR;
  Org-Mode_template --> Python_build_script
  JSON_CV_data --> Python_build_script
  Python_build_script --> Org-Mode_final
  Org-Mode_final --> Emacs
  Emacs --> CV_HTML
  Emacs --> CV_PDF
```
