from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.renderers import TemplateHTMLRenderer
from .models import Person, ConcretePersonActionHistory
from company.models import Door
from face_recognizer_src.classes.singleton_recognizer import SingletonRecognizer
from .serializers import ConcretePersonActionHistorySerializer, PersonTrackingSerializer
from datetime import timedelta, datetime


class PostConcretePersonActionHistory(APIView):
    # TODO: rewrite this code
    def post(self, request):
        response_ctx = []

        try:
            door = Door.objects.get(pk=request.data['door'])
        except Door.DoesNotExist:
            return Response("Error: Door with PK {} does not exist in database".format(request.data['door']),
                            status=status.HTTP_404_NOT_FOUND)

        file = request.FILES['file']
        image_path = file.temporary_file_path()

        # processing image and recognize person
        frame = SingletonRecognizer.get_instance().frame_adapter.process_frame(image_path)

        all_person_id_on_image, face_locations = SingletonRecognizer.get_instance().companies_recognizers[
            door.company.pk].get_face_names_and_locations(frame)

        if len(all_person_id_on_image) == 0:
            response_ctx = ['No faces detected on image']

        for person_id in all_person_id_on_image:
            is_valid, reason = validate_person(person_id, door)
            if is_valid:
                person = Person.active_objects.get(pk=person_id)

                # data_for_creation = {'person': person.pk,
                #                      'status': door.get_status_display(), 'file': file, 'door': door.pk}
                data_for_creation = {'person': person.pk,
                                     'status': door.status, 'door': door.pk,
                                     'timestamp': datetime.now(door.company.timezone)}

                action_history_serializer = ConcretePersonActionHistorySerializer(data=data_for_creation)
                if action_history_serializer.is_valid():
                    action_history_obj = action_history_serializer.save()

                    # Get a count of user's recognition  in the last five seconds
                    time_threshold = action_history_obj.timestamp - timedelta(seconds=5)
                    rec_users_queryset = ConcretePersonActionHistory.objects.filter(person=person,
                                                                                    timestamp__gte=time_threshold)
                    # If the count of user's recognition in the last five seconds >= 5 then save person tracking action
                    if rec_users_queryset.count() >= 5:
                        person_tracking_serializer = PersonTrackingSerializer(
                            data={'action_history': action_history_obj.pk})
                        if person_tracking_serializer.is_valid():
                            person_tracking_serializer.save()
                        response_ctx.append({'person': person.person_full_name,
                                             'status': door.get_status_display(), 'door_id': door.pk})
                        continue
                    else:
                        response_ctx.append({'person': person.person_full_name,
                                             'status': 'Needed count of recognition: {}'.format(
                                                 5 - rec_users_queryset.count()), 'door_id': door.pk})
                else:
                    continue

            else:
                response_ctx.append({'status': False, 'reason': reason, 'door_id': door.pk})

        return Response(response_ctx, status=status.HTTP_200_OK)


class GetPersonsByCompanyId(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'admin/includes/allowed_person.html'

    def get(self, request):
        persons = []
        if request.query_params['pk'] is not None and request.query_params['pk'] != '':
            persons = Person.active_objects.filter(company__pk=request.query_params['pk'])
        return Response({'persons': persons})


def validate_person(person_id, door_obj):
    """
    Validate person permission and comparing person's company_id and door's company_id
    :param person_id:
    :param door_obj: Door objects with camera which send request for validation
    :return: True or False and reason if person not valid
    """
    allowed_person_to_door = door_obj.allowed_person.all()

    if person_id is not 'Unknown':
        try:
            person = Person.active_objects.get(id=person_id)
        except Person.DoesNotExist:
            return False, "Error: Person with id {} does not exist in database. This person was deleted from database".format(
                person_id)

        if person in allowed_person_to_door:
            return True, 'Successful'
        elif allowed_person_to_door.count() == 0 and person.company.pk == door_obj.company.pk:
            return True, 'Successful'
        else:
            return False, "Error: Person with id {} does not exist in door's (door_id = {}) allowed person list".format(
                person_id, door_obj.pk)
    else:
        return False, "Error: Can't recognize person, person doesn't exists in database or model needed more training data"
