from datetime import datetime
import asyncio
from sqlalchemy import text, select

from kts_backend.base.base_accessor import BaseAccessor
from kts_backend.game.models import GameModel, GameScoreModel
from kts_backend.users.models import UserModel


class GameAccessor(BaseAccessor):
    async def create_game(self, chat_id):
        async with self.app.database.session.begin() as session:
            game = GameModel(created_at=datetime.now(), chat_id=chat_id, status=0, words=[])
            session.add(game)
            await session.flush()

            users = await self.app.store.users.get_users(self.app, chat_id)
            users_list = [UserModel(vk_id=player['id'], name=player['first_name'], last_name=player['last_name'])
                          for player in users]
            session.add_all(users_list)
            await session.flush()

            for user in users_list:
                gamescore = GameScoreModel(player_id=user.id, game_id=game.id, points=0, is_playing=1)
                session.add(gamescore)

    async def get_active_game_by_chat_id (self, chat_id):
        async with self.app.database.session() as session:
            query = select(GameModel).where(GameModel.chat_id == chat_id).order_by(GameModel.status.desc()).limit(1)
            res = await session.execute(query)
            return res

