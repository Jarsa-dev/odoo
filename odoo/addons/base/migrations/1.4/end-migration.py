import logging
_logger = logging.getLogger(__name__)


def migrate(cr, installed_version):
    _logger.warning('Reset base module to version 1.3')
    cr.execute("""
        UPDATE ir_module_module
        SET
        latest_version = '13.0.1.3'
        WHERE name = 'base';
    """)
