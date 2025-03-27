import time

def wpmethod(player, Player, Participant, dbq, C):
    now = time.time()
    first_time = player.participant.vars.get('first_arrival_time', now)
    remaining_time = max(0, int(C.THRESHOLD_SEC - (now - first_time)))  # in seconds
    fk_field = Player.group_id
    my_page_index = player.participant._index_in_pages

    ps = dbq(Player).join(Participant).filter(fk_field == player.group.id,
                                              ).with_entities(Participant)

    num_here = ps.filter(Participant._index_in_pages == my_page_index).count()
    num_left = C.PLAYERS_PER_GROUP - num_here
    return dict(num_left=num_left, num_here=num_here,
                seconds_left=remaining_time
                )


