from  datetime import datetime, timezone, timedelta
from rest_framework import serializers
from vote.models import Election

class ElectionSerializer(serializers.ModelSerializer):
    #supervisor = serializers.IntegerField(read_only=True)
    class Meta:
        model = Election
        fields = '__all__'

    def validate(self, data):
        print("Inside validate :")
        now_time = datetime.now(timezone(timedelta(hours=1))) # utc +1
        print("data", type(data['begin_date']), "now time",now_time)
        if data['begin_date'] > data['end_date'] :
            raise serializers.ValidationError("La date de debut doit etre anterieur a la date de fin")
        elif data['begin_date'] < now_time:
            raise serializers.ValidationError("La date de debut doit etre posterieur a la date actuelle")
        return data