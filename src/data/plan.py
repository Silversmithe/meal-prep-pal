from enum import Enum

"""
Mealplan object
"""
class MealPlan (object):

    # To determine what days of the week to create
    # currently a limit on only one-week meal plans
    DAYS_OF_WEEK = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]

    # one days worth of meals
    class DayPlan (object):

        def __init__(self) -> None:
            self.day_plan = {
                "breakfast": None,
                "lunch": None,
                "dinner": None,
                "snack": None,
                "dessert": None
            }

    def __init__(self, start_day, end_day=None) -> None:
        self.meal_plan = {}

        start_idx = 0
        # check if the start day exists
        if start_day in MealPlan.DAYS_OF_WEEK:
            start_idx = MealPlan.DAYS_OF_WEEK.index(start_day)

        end_idx = len(MealPlan.DAYS_OF_WEEK) - 1
        if end_day is not None and end_day in MealPlan.DAYS_OF_WEEK:
            end_idx = MealPlan.DAYS_OF_WEEK.index(end_day)

        if end_idx < start_idx:
            end_idx = start_idx
            
        # create a standard days of the week
        for day_idx in range(start_idx, end_idx+1):
            day = MealPlan.DAYS_OF_WEEK[day_idx]
            self.meal_plan[day] = MealPlan.DayPlan()

        print(self.meal_plan)

    def __str__(self) -> str:
        result = ""
        # create a standard days of the week
        days = self.meal_plan.keys()
        for day in days:
            day_item = self.meal_plan[day]
            current_plan = day_item.day_plan
            result += "{}:\n".format(day)
            for key in current_plan.keys():
                result += "\t{}: {}\n".format(key, current_plan[key])
        
        return result