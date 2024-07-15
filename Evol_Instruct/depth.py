base_instruction = "I want you act as a Prompt Rewriter.\r\n \
					Your objective is to rewrite a given prompt into a more complex version to make those famous AI systems (e.g., chatgpt and GPT4) a bit harder to handle.\r\n \
					But the rewritten prompt must be reasonable and must be understood and responded by humans.\r\n \
					Your rewriting cannot omit the non-text parts such as the table and code in #The Given Prompt#:. Also, please do not omit the input in #The Given Prompt#. \r\n \
					You SHOULD complicate the given prompt using the following method: \r\n\
					{} \r\n\
					You should try your best not to make the #Rewritten Prompt# become verbose, #Rewritten Prompt# can only add 10 to 20 words into #The Given Prompt#. \r\n\
					'#The Given Prompt#', '#Rewritten Prompt#', 'given prompt' and 'rewritten prompt' are not allowed to appear in #Rewritten Prompt#\r\n"


def createConstraintsPrompt(instruction):
	"""
	Creates a prompt for adding constraints/requirements to a given instruction.

	Parameters
	----------
	instruction : str
		The given instruction to which constraints/requirements will be added.

	Returns
	-------
	prompt : str
		The prompt for adding constraints/requirements to the given instruction.
	"""
	prompt = base_instruction.format("Please add one more constraints/requirements into #The Given Prompt#'")
	prompt += "#The Given Prompt#: \r\n {} \r\n".format(instruction)
	prompt += "#Rewritten Prompt#:\r\n"
	return prompt

def createDeepenPrompt(instruction):
	"""
	Creates a deepened prompt by adding a rewritten prompt to the given instruction.

	Parameters
	----------
	instruction : str
		The given prompt that contains inquiries about certain issues.

	Returns
	-------
	prompt : str
		The deepened prompt that includes the given prompt and a rewritten prompt.

	Notes
	-----
	The depth and breadth of the inquiry can be increased by adding a rewritten prompt to the given prompt.
	"""
	prompt = base_instruction.format("If #The Given Prompt# contains inquiries about certain issues, the depth and breadth of the inquiry can be increased.")
	prompt += "#The Given Prompt#: \r\n {} \r\n".format(instruction)
	prompt += "#Rewritten Prompt#:\r\n"
	return prompt

def createConcretizingPrompt(instruction):
	"""
	Creates a concretizing prompt by replacing general concepts with more specific concepts.

	Parameters
	----------
	instruction : str
		The original instruction to be concretized.

	Returns
	-------
	prompt : str
		The concretizing prompt with the given instruction and rewritten prompt.
	"""
	prompt = base_instruction.format("Please replace general concepts with more specific concepts.")
	prompt += "#The Given Prompt#: \r\n {} \r\n".format(instruction)
	prompt += "#Rewritten Prompt#:\r\n"
	return prompt

def createReasoningPrompt(instruction):
	"""
	Creates a reasoning prompt by rewriting the given prompt to explicitly request multiple-step reasoning.

	Parameters
	----------
	instruction : str
		The given prompt that needs to be rewritten.

	Returns
	-------
	prompt : str
		The rewritten prompt that explicitly requests multiple-step reasoning.
	"""
	prompt = base_instruction.format("If #The Given Prompt# can be solved with just a few simple thinking processes, you can rewrite it to explicitly request multiple-step reasoning.")
	prompt += "#The Given Prompt#: \r\n {} \r\n".format(instruction)
	prompt += "#Rewritten Prompt#:\r\n"
	return prompt