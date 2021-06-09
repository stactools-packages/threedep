import stactools.core

from stactools.threedep.metadata import Metadata

stactools.core.use_fsspec()


def register_plugin(registry):
    from stactools.threedep import commands
    registry.register_subcommand(commands.create_threedep_command)


__all__ = [Metadata]
__version__ = '0.1.5'
"""Library version"""
