from . import assigment
from . import lecture
from . import group
from . import user


#todo: hook pri ondelete

Assigment =  assigment.Model
Lecture =  lecture.Model
Group =  group.Model
User =  user.Model


__all__=["Assigment", "Lecture", "Group", "User"]