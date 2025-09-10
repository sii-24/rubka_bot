class Event:
    id: str
    date: str
    place: str
    equipment: str
    person_id: str
    comment: str
    contact: str
    user_id: str
    approved: bool
    status: int

    def __init__(self, id="0", date="", place="", equipment="", person_id="0", comment="", contact="", user_id="", approved=False, status=1):
        self.id = id
        self.date = date
        self.place = place
        self.equipment = equipment
        self.person_id = person_id
        self.comment = comment
        self.contact = contact
        self.user_id = user_id
        self.approved = approved
        self.status = status
