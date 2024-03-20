from src.model.ir import Label, Jump, CondJump


class BasicBlock:
    def __init__(self, label=None):
        self.label = label
        self.instructions = []

    def add_instruction(self, instruction):
        self.instructions.append(instruction)


def split_into_basic_blocks(instructions):
    basic_blocks = []
    current_block = BasicBlock()

    for instruction in instructions:
        # If the instruction is a label, start a new block unless it's the first
        if isinstance(instruction, Label):
            if current_block.instructions:
                basic_blocks.append(current_block)
                current_block = BasicBlock(instruction)
            else:
                current_block.label = instruction
        else:
            current_block.add_instruction(instruction)

        # If the instruction is a control flow change, end the current block
        if isinstance(instruction, (Jump, CondJump)):
            basic_blocks.append(current_block)
            current_block = BasicBlock()

    if current_block.instructions:
        basic_blocks.append(current_block)

    return basic_blocks


class FlowGraph:
    def __init__(self):
        self.blocks = []  # List of basic blocks
        self.edges = {}  # Dictionary to store edges, key is block's label, value is a list of labels

    def add_block(self, block):
        self.blocks.append(block)
        if block.label not in self.edges:
            self.edges[block.label] = []

    def add_edge(self, from_label, to_label):
        if from_label in self.edges:
            self.edges[from_label].append(to_label)
        else:
            self.edges[from_label] = [to_label]

def build_flowgraph(basic_blocks):
    flowgraph = FlowGraph()
    for block in basic_blocks:
        flowgraph.add_block(block)
        # Find the last instruction of the block to determine control flow
        last_instruction = block.instructions[-1]
        if isinstance(last_instruction, Jump):
            flowgraph.add_edge(block.label, last_instruction.label.name)
        elif isinstance(last_instruction, CondJump):
            flowgraph.add_edge(block.label, last_instruction.then_label.name)
            flowgraph.add_edge(block.label, last_instruction.else_label.name)
        # Handle sequential flow
        else:
            current_index = basic_blocks.index(block)
            if current_index < len(basic_blocks) - 1:  # Not the last block
                next_block = basic_blocks[current_index + 1]
                flowgraph.add_edge(block.label, next_block.label)

    return flowgraph

class ProgramState:
    def __init__(self):
        # Maps variable names to a set of instruction indices where it might have been defined
        self.definitions = {}

    def add_definition(self, var, instruction_index):
        if var not in self.definitions:
            self.definitions[var] = set()
        self.definitions[var].add(instruction_index)

    def merge(self, other_state):
        # Merge definitions from another state into this one
        for var, defs in other_state.definitions.items():
            if var not in self.definitions:
                self.definitions[var] = defs.copy()
            else:
                self.definitions[var].update(defs)

def perform_reaching_definitions_analysis(flowgraph):
    # Initialize program states for each basic block
    block_states = {block.label: ProgramState() for block in flowgraph.blocks}

    # Iterate over the flowgraph until the states stabilize
    changed = True
    while changed:
        changed = False
        for block in flowgraph.blocks:
            state = ProgramState()
            # Merge states from all predecessors
            for pred_label in flowgraph.edges.get(block.label, []):
                state.merge(block_states[pred_label])
            # Process instructions in the block
            for index, instruction in enumerate(block.instructions):
                if isinstance(instruction):
                    state.add_definition(instruction.var, index)
            # Check if the state has changed
            if block_states[block.label].definitions != state.definitions:
                block_states[block.label] = state
                changed = True
    return block_states

class DataFlowAnalysisFramework:
    def __init__(self, flowgraph, initial_state, transfer_function, merge_function):
        self.flowgraph = flowgraph
        self.initial_state = initial_state
        self.transfer_function = transfer_function
        self.merge_function = merge_function
        self.entry_states = {block.label: initial_state.copy() for block in flowgraph.blocks}
        self.exit_states = {block.label: initial_state.copy() for block in flowgraph.blocks}

    def analyze(self):
        changed = True
        while changed:
            changed = False
            for block in self.flowgraph.blocks:
                entry_state = self.initial_state.copy()
                for pred_label in self.flowgraph.edges.get(block.label, []):
                    entry_state = self.merge_function(entry_state, self.exit_states[pred_label])

                self.entry_states[block.label] = entry_state
                new_exit_state = self.transfer_function(entry_state, block)

                if new_exit_state != self.exit_states[block.label]:
                    self.exit_states[block.label] = new_exit_state
                    changed = True

    def reaching_definitions_transfer(entry_state, block):
        exit_state = entry_state.copy()
        # 根据 block 的指令更新 exit_state
        return exit_state

