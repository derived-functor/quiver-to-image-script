class QuiverError(Exception):
    pass


class DockerNotAvailableError(QuiverError):
    pass


class DockerDaemonNotRunningError(QuiverError):
    pass


class DockerImageNotFoundError(QuiverError):
    pass


class ClipboardEmptyError(QuiverError):
    pass


class ClipboardNotAvailableError(QuiverError):
    pass


class CompilationError(QuiverError):
    pass
