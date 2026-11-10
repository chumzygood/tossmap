"""Shared facility-question vocabulary. Unknown never means no."""
QUESTIONS = [
    ('residents_only', 'Residents only?'),
    ('id_required', 'Proof of residency or ID required?'),
    ('appointment_required', 'Appointment required?'),
    ('fee_charged', 'Is a fee charged?'),
    ('tires', 'Accepts tires?'),
    ('paint', 'Accepts paint?'),
    ('e_waste', 'Accepts e-waste?'),
    ('batteries', 'Accepts batteries?'),
    ('motor_oil', 'Accepts motor oil?'),
    ('household_chemicals', 'Accepts household chemicals?'),
    ('quantity_limits', 'Quantity limits?'),
    ('businesses_accepted', 'Businesses accepted?'),
]
UNKNOWN = 'not stated by source'
def unknown_questions():
    return {key: {'answer': UNKNOWN, 'evidence': ''} for key, _ in QUESTIONS}
