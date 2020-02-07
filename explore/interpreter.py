from django.urls import reverse
from .models import Activity

class Interpreter(object):

    ALLOWED_CONNECTIONS = [
        'north',
        'south',
        'east',
        'west',
        'up',
        'down'
    ]

    def __init__(self, models):
        # Save models
        self.models = models

    def execute(self, command):

        # Parse command into words
        words = command.split(' ')
        if len(words) > 0:
            operator = words[0]
        if len(words) > 1:
            target = words[1]

        # Determine type of command
        if operator == 'create':
            if target == 'connection':
                title = ' '.join(words[2:])
                if Interpreter.validate_connection(title):
                    kwargs = {
                        'source_id': self.models['area'].id,
                        'title': title,
                    }
                    return reverse('explore:new_connection', kwargs=kwargs)
                else:
                    activity = Activity(
                        area=self.models['area'],
                        creator=self.models['user'],
                        creator_only=True,
                        activity_text='Connections must be one of: ' + ', '.join(Interpreter.ALLOWED_CONNECTIONS) + '.',
                    )
                    activity.save()
                    return reverse('explore:area', args=[self.models['area'].id])
        elif operator == 'edit':
            if target == 'description':
                return reverse('explore:area_description', args=[self.models['area'].id])
        else:
            # If no command, leave a message
            activity_text = f'{self.models["user"].username}: {command}'
            activity = Activity(
                creator=self.models['user'],
                area=self.models['area'],
                activity_text=activity_text)
            activity.save()

    def validate_connection(title):
        return len(title) > 0 and title in Interpreter.ALLOWED_CONNECTIONS
