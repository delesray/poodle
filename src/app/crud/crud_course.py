async def get_by_id(course_id):
    #Teachers must be able to view their own courses
    pass

async def get_courses(existing_teacher):
    #Teachers must be able to view their own courses
    pass

async def create_course(new_course, existing_teacher):
    pass

async def edit_course(course_id, course_update):
    pass

async def get_all_courses(
    #Admins could be able to view a list with all public and premium courses, the number of students in them and their rating
        page: int,
        size: int,
        search: str = None,
        owner_id: int = None,
        student_id: int = None
        ):
    pass