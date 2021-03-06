from .... import sim_options as o
from ....state_plugins.sim_action_object import SimActionObject
from ....state_plugins.sim_action import SimActionData


def SimIRStmt_PutI(engine, state, stmt):
    # value to put
    with state.history.subscribe_actions() as data_deps:
        data = engine.handle_expression(state, stmt.data)
    expr = data.raw_to_bv()

    # reg array data
    ix = engine.handle_expression(state, stmt.ix)
    array_size = len(expr) // state.arch.byte_width
    array_base = stmt.descr.base
    array_index = (ix + stmt.bias) % stmt.descr.nElems
    offset = array_base + array_index * array_size

    # track the put
    if o.TRACK_REGISTER_ACTIONS in state.options:
        data_ao = SimActionObject(expr, deps=data_deps, state=state)
        size_ao = SimActionObject(len(data))
        a = SimActionData(state, SimActionData.REG, SimActionData.WRITE, addr=offset, data=data_ao, size=size_ao)
        state.history.add_action(a)
    else:
        a = None

    # do the put (if we should)
    if o.DO_PUTS in state.options:
        state.registers.store(offset, expr, action=a)
