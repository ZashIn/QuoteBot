import asyncio

from bot import QuoteBot

async def upgrade_db():
    async with QuoteBot.db_connect(None) as con:
        if (row := await con.execute_fetchone("SELECT COUNT(*) FROM pragma_table_info('highlight') WHERE name='guild_id'")) and row[0]:
            return
        await con.executescript(
            """
            CREATE TABLE h_temp (
                user_id INTEGER NOT NULL,
                query TEXT NOT NULL,
                guild_id INTEGER NOT NULL DEFAULT 0,
                PRIMARY KEY (user_id, query, guild_id)
            );
            INSERT INTO h_temp
                SELECT user_id, query, 0 FROM highlight
            ;
            DROP TABLE highlight;
            ALTER TABLE h_temp
                RENAME TO highlight
            ;
            CREATE TRIGGER
                IF NOT EXISTS delete_guild_highlights
                    AFTER DELETE ON guild
                BEGIN
                    DELETE FROM highlight
                    WHERE guild_id = old.guild_id;
                END
            ;
            """
        )

asyncio.run(upgrade_db())
