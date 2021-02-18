import datetime
import requests
import traceback
from psycopg2 import extras

from api import settings, database
from api.models.ballchasing import ReplayGroup


class Ballchasing:

    BASE_URL = 'https://ballchasing.com/api'

    def send_request(self, url, headers={}, method=settings.REQUEST_METHOD['get'], params=None):
        """リクエスト送信

        Args:
            url (str): URL
            headers (dict): Header情報
            method (string): Method

        Returns:
            Response: レスポンス
        """

        request_url = self.BASE_URL + url
        base_headers = {
            'Authorization': settings.BCS_API_KEY
        }
        req_headers = {**base_headers, **headers}

        if method == settings.REQUEST_METHOD['get']:
            return requests.get(request_url, headers=req_headers, params=params)

    def get_group(self, group_id):
        """グループデータ取得

        Args:
            group_id (int): グループID

        Returns:
            Group: グループデータ
        """

        url = f'/groups/{group_id}'
        r = self.send_request(url)
        d = r.json()
        replay_group = ReplayGroup(**r.json())
        return replay_group

    def get_group_children(self, group_id):
        """グループの子グループデータ取得

        Args:
            group_id (int): 親グループID

        Returns:
            List[Group]: 子グループデータ
        """

        url = f'/groups'
        params = {
            'group': group_id,
            'sort-by': 'created',
            'sort-dir': 'asc'
        }
        r = self.send_request(url, params=params)
        replay_groups = []
        for x in r.json()['list']:
            group = self.get_group(x['id'])
            replay_groups.append(group)
        return replay_groups

    def init_db(self, group_id, background_task_id):
        """データベース初期化

        Args:
            group_id (int): 親グループID
        """
        with database.get_connection() as conn:
            with conn.cursor() as cursor:
                # Background Task Status
                values = (background_task_id, 'ballchasing init_db started', datetime.datetime.now())
                cursor.execute("INSERT INTO background_tasks (id, status, created_at) VALUES (%s, %s, %s)", values)

        st = None
        with database.get_connection() as conn:
            with conn.cursor() as cursor:
                try:
                    tables = [
                        'groups',
                        'players',
                        'cumulatives',
                        'cumulative_cores',
                        'cumulative_boosts',
                        'cumulative_movements',
                        'cumulative_positionings',
                        'cumulative_demos',
                        'game_averages',
                        'game_average_cores',
                        'game_average_boosts',
                        'game_average_movements',
                        'game_average_positionings',
                        'game_average_demos'
                    ]
                    for table in tables:
                        cursor.execute(f'TRUNCATE TABLE {table}')

                    # グループ情報書き換え
                    group = self.get_group(group_id)
                    self.init_db_group(cursor, group, None)

                    cumulative_values = {
                        'base': [],
                        'core': [],
                        'boost': [],
                        'movement': [],
                        'positioning': [],
                        'demo': [],
                    }
                    game_average_values = {
                        'base': [],
                        'core': [],
                        'boost': [],
                        'movement': [],
                        'positioning': [],
                        'demo': [],
                    }

                    # プレイヤー情報書き換え
                    for player in group.players:
                        self.init_db_player(cursor, player)
                        self.init_db_cumulative(cursor, group, player, cumulative_values)
                        self.init_db_game_average(cursor, group, player, game_average_values)

                    # 子グループ情報書き換え
                    group_children = self.get_group_children(group_id)
                    for child in group_children:
                        self.init_db_group(cursor, child, group_id)

                        for player in child.players:
                            self.init_db_cumulative(cursor, child, player, cumulative_values)
                            self.init_db_game_average(cursor, child, player, game_average_values)

                    # Bulk Insert
                    self.bulk_insert_cumulative(cursor, cumulative_values)
                    self.bulk_insert_game_average(cursor, game_average_values)

                except:
                    st = traceback.format_exc()

        with database.get_connection() as conn:
            with conn.cursor() as cursor:
                # Background Task Status
                status = 'ballchasing init_db ended' if st is None else f'ballchasing init_db error: {st}'
                values = (background_task_id, status, datetime.datetime.now())
                cursor.execute("INSERT INTO background_tasks (id, status, created_at) VALUES (%s, %s, %s)", values)

    def create_format_str(self, values):
        """フォーマット文字列生成

        Args:
            values (array): values

        Returns:
            str: フォーマット文字列
        """
        return "%s" + ", %s" * (len(values) - 1)

    def init_db_group(self, cursor, group, parent_group_id):
        """グループ情報初期化

        Args:
            cursor (obj): cursor
            group (ReplayGroup): グループ情報
            parent_group_id (str): 親グループID
        """
        values = (group.id, group.name, parent_group_id, group.created)
        format_str = self.create_format_str(values)
        cursor.execute(f"INSERT INTO groups (id, name, parent_group_id, created) VALUES ({format_str})", values)

    def init_db_player(self, cursor, player):
        """プレイヤー情報初期化

        Args:
            cursor (obj): cursor
            player (Player): プレイヤー情報
        """
        values = (player.id, player.name, player.team, player.platform)
        format_str = self.create_format_str(values)
        cursor.execute(f"INSERT INTO players (id, name, team_id, platform) VALUES ({format_str})", values)

    def get_next_seq(self, cursor, seq_name):
        """SEQ取得

        Args:
            cursor (obj): cursor
            seq_name (str): シーケンス名

        Returns:
            int: SEQ
        """
        cursor.execute(f"SELECT NEXTVAL('{seq_name}')")
        return cursor.fetchone()[0]

    def init_db_cumulative(self, cursor, group, player, cumulative_values):
        """累計成績初期化

        Args:
            cursor (obj): cursor
            group (ReplayGroup): グループ情報
            player (Player): プレイヤー情報
        """
        id = self.get_next_seq(cursor, 'cumulative_id_seq')
        group_id = group.id
        player_id = player.id
        cumulative = player.cumulative
        core_id = self.get_next_seq(cursor, 'cumulative_core_id_seq')
        boost_id = self.get_next_seq(cursor, 'cumulative_boost_id_seq')
        movement_id = self.get_next_seq(cursor, 'cumulative_movement_id_seq')
        positioning_id = self.get_next_seq(cursor, 'cumulative_positioning_id_seq')
        demo_id = self.get_next_seq(cursor, 'cumulative_demo_id_seq')

        values = (
            id,
            group_id,
            player_id,
            cumulative.games,
            cumulative.wins,
            cumulative.win_percentage,
            cumulative.play_duration,
            core_id,
            boost_id,
            movement_id,
            positioning_id,
            demo_id
        )
        cumulative_values['base'].append(values)

        # Core, Boost, Movement, Positioning, Demo
        cumulative_values['core'].append(self.init_db_cumulative_core(cursor, player, core_id))
        cumulative_values['boost'].append(self.init_db_cumulative_boost(cursor, player, boost_id))
        cumulative_values['movement'].append(self.init_db_cumulative_movement(cursor, player, movement_id))
        cumulative_values['positioning'].append(self.init_db_cumulative_positioning(cursor, player, positioning_id))
        cumulative_values['demo'].append(self.init_db_cumulative_demo(cursor, player, demo_id))

    def init_db_cumulative_core(self, cursor, player, core_id):
        """累計成績初期化（Core）

        Args:
            cursor (obj): cursor
            group (ReplayGroup): グループ情報
            player (Player): プレイヤー情報
        """
        core = player.cumulative.core
        values = (
            core_id,
            core.shots,
            core.shots_against,
            core.goals,
            core.goals_against,
            core.saves,
            core.assists,
            core.score,
            core.mvp,
            core.shooting_percentage
        )
        return values

    def init_db_cumulative_boost(self, cursor, player, boost_id):
        """累計成績初期化（Boost）

        Args:
            cursor (obj): cursor
            group (ReplayGroup): グループ情報
            player (Player): プレイヤー情報
        """
        boost = player.cumulative.boost
        values = (
            boost_id,
            boost.bpm,
            boost.bcpm,
            boost.avg_amount,
            boost.amount_collected,
            boost.amount_stolen,
            boost.amount_collected_big,
            boost.amount_stolen_big,
            boost.amount_collected_small,
            boost.amount_stolen_small,
            boost.count_collected_big,
            boost.count_stolen_big,
            boost.count_collected_small,
            boost.count_stolen_small,
            boost.time_zero_boost,
            boost.percent_zero_boost,
            boost.time_full_boost,
            boost.percent_full_boost,
            boost.amount_overfill,
            boost.amount_overfill_stolen,
            boost.amount_used_while_supersonic,
            boost.time_boost_0_25,
            boost.time_boost_25_50,
            boost.time_boost_50_75,
            boost.time_boost_75_100,
            boost.percent_boost_0_25,
            boost.percent_boost_25_50,
            boost.percent_boost_50_75,
            boost.percent_boost_75_100,
        )
        return values

    def init_db_cumulative_movement(self, cursor, player, movement_id):
        """累計成績初期化（Movement）

        Args:
            cursor (obj): cursor
            group (ReplayGroup): グループ情報
            player (Player): プレイヤー情報
        """
        movement = player.cumulative.movement
        values = (
            movement_id,
            movement.avg_speed,
            movement.total_distance,
            movement.time_supersonic_speed,
            movement.time_boost_speed,
            movement.time_slow_speed,
            movement.time_ground,
            movement.time_low_air,
            movement.time_high_air,
            movement.time_powerslide,
            movement.count_powerslide,
            movement.avg_powerslide_duration,
            movement.avg_speed_percentage,
            movement.percent_slow_speed,
            movement.percent_boost_speed,
            movement.percent_supersonic_speed,
            movement.percent_ground,
            movement.percent_low_air,
            movement.percent_high_air,
        )
        return values

    def init_db_cumulative_positioning(self, cursor, player, positioning_id):
        """累計成績初期化（Positioning）

        Args:
            cursor (obj): cursor
            group (ReplayGroup): グループ情報
            player (Player): プレイヤー情報
        """
        positioning = player.cumulative.positioning
        values = (
            positioning_id,
            positioning.avg_distance_to_ball,
            positioning.avg_distance_to_ball_possession,
            positioning.avg_distance_to_ball_no_possession,
            positioning.time_defensive_third,
            positioning.time_neutral_third,
            positioning.time_offensive_third,
            positioning.time_defensive_half,
            positioning.time_offensive_half,
            positioning.time_behind_ball,
            positioning.time_infront_ball,
            positioning.time_most_back,
            positioning.time_most_forward,
            positioning.goals_against_while_last_defender,
            positioning.time_closest_to_ball,
            positioning.time_farthest_from_ball,
            positioning.percent_defensive_third,
            positioning.percent_offensive_third,
            positioning.percent_neutral_third,
            positioning.percent_defensive_half,
            positioning.percent_offensive_half,
            positioning.percent_behind_ball,
            positioning.percent_infront_ball,
        )
        return values

    def init_db_cumulative_demo(self, cursor, player, demo_id):
        """累計成績初期化（Demo）

        Args:
            cursor (obj): cursor
            player (Player): プレイヤー情報
            demo_id (int): seq
        """
        demo = player.cumulative.demo
        values = (
            demo_id,
            demo.inflicted,
            demo.taken
        )
        return values

    def init_db_game_average(self, cursor, group, player, game_average_values):
        """平均成績初期化

        Args:
            cursor (obj): cursor
            group (ReplayGroup): グループ情報
            player (Player): プレイヤー情報
        """
        id = self.get_next_seq(cursor, 'game_average_id_seq')
        group_id = group.id
        player_id = player.id
        game_average = player.game_average
        core_id = self.get_next_seq(cursor, 'game_average_core_id_seq')
        boost_id = self.get_next_seq(cursor, 'game_average_boost_id_seq')
        movement_id = self.get_next_seq(cursor, 'game_average_movement_id_seq')
        positioning_id = self.get_next_seq(cursor, 'game_average_positioning_id_seq')
        demo_id = self.get_next_seq(cursor, 'game_average_demo_id_seq')

        values = (
            id,
            group_id,
            player_id,
            core_id,
            boost_id,
            movement_id,
            positioning_id,
            demo_id
        )
        game_average_values['base'].append(values)

        # Core, Boost, Movement, Positioning, Demo
        game_average_values['core'].append(self.init_db_game_average_core(cursor, player, core_id))
        game_average_values['boost'].append(self.init_db_game_average_boost(cursor, player, boost_id))
        game_average_values['movement'].append(self.init_db_game_average_movement(cursor, player, movement_id))
        game_average_values['positioning'].append(self.init_db_game_average_positioning(cursor, player, positioning_id))
        game_average_values['demo'].append(self.init_db_game_average_demo(cursor, player, demo_id))

    def init_db_game_average_core(self, cursor, player, core_id):
        """平均成績初期化（Core）

        Args:
            cursor (obj): cursor
            group (ReplayGroup): グループ情報
            player (Player): プレイヤー情報
        """
        core = player.game_average.core
        values = (
            core_id,
            core.shots,
            core.shots_against,
            core.goals,
            core.goals_against,
            core.saves,
            core.assists,
            core.score,
            core.mvp,
            core.shooting_percentage
        )
        return values

    def init_db_game_average_boost(self, cursor, player, boost_id):
        """平均成績初期化（Boost）

        Args:
            cursor (obj): cursor
            group (ReplayGroup): グループ情報
            player (Player): プレイヤー情報
        """
        boost = player.game_average.boost
        values = (
            boost_id,
            boost.bpm,
            boost.bcpm,
            boost.avg_amount,
            boost.amount_collected,
            boost.amount_stolen,
            boost.amount_collected_big,
            boost.amount_stolen_big,
            boost.amount_collected_small,
            boost.amount_stolen_small,
            boost.count_collected_big,
            boost.count_stolen_big,
            boost.count_collected_small,
            boost.count_stolen_small,
            boost.time_zero_boost,
            boost.percent_zero_boost,
            boost.time_full_boost,
            boost.percent_full_boost,
            boost.amount_overfill,
            boost.amount_overfill_stolen,
            boost.amount_used_while_supersonic,
            boost.time_boost_0_25,
            boost.time_boost_25_50,
            boost.time_boost_50_75,
            boost.time_boost_75_100,
            boost.percent_boost_0_25,
            boost.percent_boost_25_50,
            boost.percent_boost_50_75,
            boost.percent_boost_75_100,
        )
        return values

    def init_db_game_average_movement(self, cursor, player, movement_id):
        """平均成績初期化（Movement）

        Args:
            cursor (obj): cursor
            group (ReplayGroup): グループ情報
            player (Player): プレイヤー情報
        """
        movement = player.game_average.movement
        values = (
            movement_id,
            movement.avg_speed,
            movement.total_distance,
            movement.time_supersonic_speed,
            movement.time_boost_speed,
            movement.time_slow_speed,
            movement.time_ground,
            movement.time_low_air,
            movement.time_high_air,
            movement.time_powerslide,
            movement.count_powerslide,
            movement.avg_powerslide_duration,
            movement.avg_speed_percentage,
            movement.percent_slow_speed,
            movement.percent_boost_speed,
            movement.percent_supersonic_speed,
            movement.percent_ground,
            movement.percent_low_air,
            movement.percent_high_air,
        )
        return values

    def init_db_game_average_positioning(self, cursor, player, positioning_id):
        """平均成績初期化（Positioning）

        Args:
            cursor (obj): cursor
            group (ReplayGroup): グループ情報
            player (Player): プレイヤー情報
        """
        positioning = player.game_average.positioning
        values = (
            positioning_id,
            positioning.avg_distance_to_ball,
            positioning.avg_distance_to_ball_possession,
            positioning.avg_distance_to_ball_no_possession,
            positioning.time_defensive_third,
            positioning.time_neutral_third,
            positioning.time_offensive_third,
            positioning.time_defensive_half,
            positioning.time_offensive_half,
            positioning.time_behind_ball,
            positioning.time_infront_ball,
            positioning.time_most_back,
            positioning.time_most_forward,
            positioning.goals_against_while_last_defender,
            positioning.time_closest_to_ball,
            positioning.time_farthest_from_ball,
            positioning.percent_defensive_third,
            positioning.percent_offensive_third,
            positioning.percent_neutral_third,
            positioning.percent_defensive_half,
            positioning.percent_offensive_half,
            positioning.percent_behind_ball,
            positioning.percent_infront_ball,
        )
        return values

    def init_db_game_average_demo(self, cursor, player, demo_id):
        """平均成績初期化（Demo）

        Args:
            cursor (obj): cursor
            player (Player): プレイヤー情報
            demo_id (int): seq
        """
        demo = player.game_average.demo
        values = (
            demo_id,
            demo.inflicted,
            demo.taken
        )
        return values

    def bulk_insert_cumulative(self, cursor, values):
        """累計成績 BULK INSERT

        Args:
            cursor ([type]): [description]
            values ([type]): [description]
        """
        extras.execute_values(
            cursor, "INSERT INTO cumulatives (id, group_id, player_id, games, wins, win_percentage, play_duration, core_id, boost_id, movement_id, positioning_id, demo_id) VALUES %s", values['base'])
        extras.execute_values(
            cursor, "INSERT INTO cumulative_cores (id, shots, shots_against, goals, goals_against, saves, assists, score, mvp, shooting_percentage) VALUES %s", values['core'])
        extras.execute_values(
            cursor, "INSERT INTO cumulative_boosts (id, bpm, bcpm, avg_amount, amount_collected, amount_stolen, amount_collected_big, amount_stolen_big, amount_collected_small, amount_stolen_small, count_collected_big, count_stolen_big, count_collected_small, count_stolen_small, time_zero_boost, percent_zero_boost, time_full_boost, percent_full_boost, amount_overfill, amount_overfill_stolen, amount_used_while_supersonic, time_boost_0_25, time_boost_25_50, time_boost_50_75, time_boost_75_100, percent_boost_0_25, percent_boost_25_50, percent_boost_50_75, percent_boost_75_100) VALUES %s", values['boost'])
        extras.execute_values(
            cursor, "INSERT INTO cumulative_movements (id, avg_speed, total_distance, time_supersonic_speed, time_boost_speed, time_slow_speed, time_ground, time_low_air, time_high_air, time_powerslide, count_powerslide, avg_powerslide_duration, avg_speed_percentage, percent_slow_speed, percent_boost_speed, percent_supersonic_speed, percent_ground, percent_low_air, percent_high_air) VALUES %s", values['movement'])
        extras.execute_values(
            cursor, "INSERT INTO cumulative_positionings (id, avg_distance_to_ball, avg_distance_to_ball_possession, avg_distance_to_ball_no_possession, time_defensive_third, time_neutral_third, time_offensive_third, time_defensive_half, time_offensive_half, time_behind_ball, time_infront_ball, time_most_back, time_most_forward, goals_against_while_last_defender, time_closest_to_ball, time_farthest_from_ball, percent_defensive_third, percent_offensive_third, percent_neutral_third, percent_defensive_half, percent_offensive_half, percent_behind_ball, percent_infront_ball) VALUES %s", values['positioning'])
        extras.execute_values(
            cursor, "INSERT INTO cumulative_demos (id, inflicted, taken) VALUES %s", values['demo'])

    def bulk_insert_game_average(self, cursor, values):
        """平均成績 BULK INSERT

        Args:
            cursor ([type]): [description]
            values ([type]): [description]
        """
        extras.execute_values(
            cursor, "INSERT INTO game_averages (id, group_id, player_id, core_id, boost_id, movement_id, positioning_id, demo_id) VALUES %s", values['base'])
        extras.execute_values(
            cursor, "INSERT INTO game_average_cores (id, shots, shots_against, goals, goals_against, saves, assists, score, mvp, shooting_percentage) VALUES %s", values['core'])
        extras.execute_values(
            cursor, "INSERT INTO game_average_boosts (id, bpm, bcpm, avg_amount, amount_collected, amount_stolen, amount_collected_big, amount_stolen_big, amount_collected_small, amount_stolen_small, count_collected_big, count_stolen_big, count_collected_small, count_stolen_small, time_zero_boost, percent_zero_boost, time_full_boost, percent_full_boost, amount_overfill, amount_overfill_stolen, amount_used_while_supersonic, time_boost_0_25, time_boost_25_50, time_boost_50_75, time_boost_75_100, percent_boost_0_25, percent_boost_25_50, percent_boost_50_75, percent_boost_75_100) VALUES %s", values['boost'])
        extras.execute_values(
            cursor, "INSERT INTO game_average_movements (id, avg_speed, total_distance, time_supersonic_speed, time_boost_speed, time_slow_speed, time_ground, time_low_air, time_high_air, time_powerslide, count_powerslide, avg_powerslide_duration, avg_speed_percentage, percent_slow_speed, percent_boost_speed, percent_supersonic_speed, percent_ground, percent_low_air, percent_high_air) VALUES %s", values['movement'])
        extras.execute_values(
            cursor, "INSERT INTO game_average_positionings (id, avg_distance_to_ball, avg_distance_to_ball_possession, avg_distance_to_ball_no_possession, time_defensive_third, time_neutral_third, time_offensive_third, time_defensive_half, time_offensive_half, time_behind_ball, time_infront_ball, time_most_back, time_most_forward, goals_against_while_last_defender, time_closest_to_ball, time_farthest_from_ball, percent_defensive_third, percent_offensive_third, percent_neutral_third, percent_defensive_half, percent_offensive_half, percent_behind_ball, percent_infront_ball) VALUES %s", values['positioning'])
        extras.execute_values(
            cursor, "INSERT INTO game_average_demos (id, inflicted, taken) VALUES %s", values['demo'])

    def get_scores_by_days(self):
        """Dayごとのスコア取得
        """

        sql = """
            select
                grp.name as group_name,
                ply.name as player_name,
                cml.wins,
                cml_core.score,
                cml_core.goals,
                cml_core.shots,
                cml_core.shooting_percentage,
                cml_core.assists,
                cml_core.saves,
                grp.created as group_created
            from
                groups grp
            inner join cumulatives cml on
                grp.id = cml.group_id
            inner join cumulative_cores cml_core on
                cml.core_id = cml_core.id
            inner join players ply on
                cml.player_id = ply.id
            where
                grp.parent_group_id is not null
            order by
                grp.created, cml_core.score desc
        """
        with database.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(sql)
                columns = [column[0] for column in cursor.description]
                results = []
                for row in cursor.fetchall():
                    results.append(dict(zip(columns, row)))
                return results

    def get_scores_all(self):
        """全試合スコア取得
        """

        sql = """
            select
                tm.id as team_id,
                tm.name as team_name,
                ply.name as player_name,
                cml.wins,
                cml_core.score,
                cml_core.goals,
                cml_core.shots,
                cml_core.shooting_percentage,
                cml_core.assists,
                cml_core.saves,
                cml_demo.taken as demos,
                (cml.wins / (select max(wins) from cumulatives) * 100) wins_parameter,
                (cml_core.score / (select max(score) from cumulative_cores) * 100) score_parameter,
                (cml_core.goals / (select max(goals) from cumulative_cores) * 100) goals_parameter,
                (cml_core.shots / (select max(shots) from cumulative_cores) * 100) shots_parameter,
                (cml_core.shooting_percentage / (select max(shooting_percentage) from cumulative_cores) * 100) shooting_percentage_parameter,
                (cml_core.assists / (select max(assists) from cumulative_cores) * 100) assists_parameter,
                (cml_core.saves / (select max(saves) from cumulative_cores) * 100) saves_parameter,
                (cml_demo.taken / (select max(taken) from cumulative_demos) * 100) demos_parameter
            from
                groups grp
            inner join cumulatives cml on
                grp.id = cml.group_id
            inner join cumulative_cores cml_core on
                cml.core_id = cml_core.id
            inner join cumulative_demos cml_demo on
                cml.demo_id = cml_demo.id
            inner join players ply on
                cml.player_id = ply.id
            inner join teams tm on
                tm.bc_team_id = ply.team_id
            where
                grp.parent_group_id is null
            order by
                cml_core.score desc
        """
        with database.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(sql)
                columns = [column[0] for column in cursor.description]
                results = []
                for row in cursor.fetchall():
                    results.append(dict(zip(columns, row)))
                return results
