from hr_game.data.employee import EmployeeDelta


def score_delta(llm,conversation)->EmployeeDelta:
    structured_llm = llm.with_structured_output(EmployeeDelta)
    delta = structured_llm.invoke(
        f"""
        You are a grader of HR person responses to stressful or positive situations.
        It is important to be critical to help the HR person grow but also to be optimistic.

        We grade employees on a set of different attributes. Many of them are negative but
        these exist on a spectrum. If an employee say has a positive interaction
        then they might have negative values for a rage trait which we interpret as agreeableness.

        Here are our scoring fields = {EmployeeDelta.model_fields.keys()}
        if a field isn't relevant to the conversion giving it a zero is ok.
        Please read the conversation between employee and HR person.
        Then score how the employees attitude might have changed.
        Score specific to the attributes listed.

        Please anticipate how what the HR person said may affect the employee.
        Also include the employees response in your grade.

        Grades can be positive or negative.
        Here is the conversation:

        {conversation}
        """
    )
    return delta