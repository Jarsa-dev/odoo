from openupgradelib import openupgrade


def fix_lang_constraints(env):
    """Avoid error on normal update process due to the removal + re-addition of
    constraints.
    """
    openupgrade.logged_query(
        env.cr, """ALTER TABLE ir_translation
        DROP CONSTRAINT ir_translation_lang_fkey_res_lang
        """,
    )


@openupgrade.migrate(use_env=True)
def migrate(env, version):
    fix_lang_constraints(env)
