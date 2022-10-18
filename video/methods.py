
def wpmethod(player, Player, Participant, dbq, C):
    fk_field = Player.group_id
    my_page_index = player.participant._index_in_pages

    ps = dbq(Player).join(Participant).filter(fk_field == player.group.id,
                                              ).with_entities(Participant)

    num_here = ps.filter(Participant._index_in_pages == my_page_index).count()
    num_left = C.PLAYERS_PER_GROUP - num_here
    return dict(num_left=num_left, num_here=num_here)