import stactools.core
from stactools.cli.registry import Registry

from stactools.threedep.metadata import Metadata

stactools.core.use_fsspec()


def register_plugin(registry: Registry) -> None:
    from stactools.threedep import commands

    registry.register_subcommand(commands.create_threedep_command)


__all__ = ["Metadata"]
__version__ = "0.2.0"
"""Library version"""
