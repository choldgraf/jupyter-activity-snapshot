import nox

nox.options.reuse_existing_virtualenvs = True

@nox.session()
def lab(session):
    """Run JupyterLab in this environment."""
    session.install("-r", "requirements.txt")
    session.run("jupyter", "lab")
