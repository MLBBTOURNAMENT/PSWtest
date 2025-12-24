from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class ParticipantProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=150)
    school = models.CharField(max_length=200)
    day = models.PositiveSmallIntegerField(choices=((1, 'Hari 1'), (2, 'Hari 2')), default=1)
    blocked = models.BooleanField(default=False)
    out_of_app_count = models.PositiveIntegerField(default=0)
    raw_password = models.CharField(max_length=50, blank=True)  # Untuk ditampilkan di kartu
    
    def __str__(self):
        return self.full_name

class Tryout(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    subjects = models.CharField(max_length=255, help_text="Pisahkan dengan · contoh: Matematika · Fisika · Kimia")
    publish_time = models.DateTimeField()
    work_time_minutes = models.PositiveIntegerField(help_text="Durasi ujian dalam menit")
    is_published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['publish_time']
    
    def __str__(self):
        return self.title
    
    def is_accessible(self):
        return self.is_published and timezone.now() >= self.publish_time

class Question(models.Model):
    tryout = models.ForeignKey(Tryout, on_delete=models.CASCADE, related_name='questions')
    number = models.PositiveIntegerField()
    text = models.TextField()
    option_a = models.TextField()
    option_b = models.TextField()
    option_c = models.TextField()
    option_d = models.TextField()
    correct_option = models.CharField(
        max_length=1,
        choices=(('A','A'),('B','B'),('C','C'),('D','D'))
    )
    score = models.FloatField(default=1.0)  # skor per soal

    class Meta:
        ordering = ['number']
        unique_together = ['tryout', 'number']

class ParticipantTryout(models.Model):
    participant = models.ForeignKey(ParticipantProfile, on_delete=models.CASCADE)
    tryout = models.ForeignKey(Tryout, on_delete=models.CASCADE)
    started_at = models.DateTimeField(null=True, blank=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    is_finished = models.BooleanField(default=False)
    out_of_app_count = models.PositiveIntegerField(default=0)
    score = models.FloatField(null=True, blank=True)         # nilai total
    max_score = models.FloatField(null=True, blank=True)     # total skor maksimum
    
    class Meta:
        unique_together = ['participant', 'tryout']
    
    def __str__(self):
        return f"{self.participant.full_name} - {self.tryout.title}"

class ParticipantAnswer(models.Model):
    participant_tryout = models.ForeignKey(ParticipantTryout, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_option = models.CharField(max_length=1, choices=(('A','A'),('B','B'),('C','C'),('D','D')), null=True, blank=True)
    answered_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['participant_tryout', 'question']
    
    def __str__(self):
        return f"{self.participant_tryout.participant.full_name} - Q{self.question.number}"
