# Jupyter Community Activity

This is a collection of Jupyter Notebooks that are **templatized** and meant to be run with [the papermill library](https://github.com/nteract/papermill).
It is automatically run each day via a CRON job on GitHub actions, and generates a website with reports for various communities in the Jupyter ecosystem at https://predictablynoisy.com/jupyter-activity-snapshot/.

## Structure of this repository

- **`monthly_update/run_template.ipynb`** - a "controller" notebook that manages the execution and report generation of template notebooks. Start here.
- **`monthly_update/templates`** - contains template notebooks that generate reports about activity over a few months of time (by default, 3 months).
- **`monthly_updates/data/`** - GitHub activity data that is stored as a part of executing notebook data "fetch" operations. This data is then re-used by report notebooks.
- **`monthly_updates/generated/`** - Outputs from running papermill on the template notebooks, this is bundled up in a Jupyter Book for display purposes.

Other folders are out of date, and left-over from prototyping different kinds of reports. Feel free to look at them for inspiration but don't expect them to work!

## Viewing the reports

The reports are [best viewed on nbviewer](https://nbviewer.jupyter.org/github/choldgraf/jupyter-activity-snapshot/blob/master/reports/). You'll see a few folders representing activity
in different moments in time. Click on the folder and then on the report that
you'd like to see.

**A caveat**: The data in these reports is just what could be (relatively) easily
scraped from the GitHub and Discourse APIs. That means we are missing a lot of really
important activity that is difficult to scrape automatically. Don't treat the numbers
in these reports as the total truth - they are just one view on the complex web of
activity that is the Jupyter community.

Note, if the information on a page looks outdated, try flushing the nbviewer cache with `?flush_cache=true` in the URL.
