from django.core.management.base import BaseCommand
from accounts.models import Districts, Province

class Command(BaseCommand): 
    def handle(self, *args, **kwargs):
        d_list = [
            {
                'Province No. 1':[
                    'Bhojpur', 'Dhankuta', 'Ilam', 'Jhapa', 'Khotang', 'Morang', 'Okhaldhunga', 'Panchthar', 'Sankhuwasabha',
                    'Solukhumbu', 'Sunsari', 'Taplejung', 'Terhathum', 'Udayapur']
            },
            {'Province No. 2':[
                'Bara', 'Dhanusa', 'Mahottari','Parsa', 'Rautahat', 'Saptari', 'Sarlahi', 'Siraha']
            },
            {
                'Bagmati Pradesh':[
                'Bhaktapur', 'Chitwan', 'Dhading', 'Dolakha', 'Kathmandu', 'KavrePalanchok','Lalitpur', 'Makwanpur',
                'Nuwakot', 'Ramechap', 'Rasuwa', 'Sindhuli', 'Sindhupalchok']
            },
            {
                'Gandaki Pradesh':[
                'Baglung', 'Gorkha', 'Kaski', 'Lamjung', 'Manang','Mustang', 'Myagdi', 'Nawalpur', 'Parbat', 'Syangja',
                'Tahanun']
            },
            {
                'Province No. 5':[
                'Arghakhanchi', 'Banke', 'Bardiya', 'Dang Deukhuri', 'Eastern Rukum','Gulmi', 'Kapilvastu', 'Palpa',
                'Parasi', 'Pyuthan', 'Rolpa', 'Rupendehi']
            },
            {
                'Karnali Pradesh': [
                    'Dailekh', 'Dolpa', 'Humla', 'Jajarkot','Jumla', 'Kalikot', 'Mugu', 'Salyan', 'Surkhet', 'Western Rukum']
            },
            {
                'Sudurpashchim Pradesh': ['Accham', 'Baitadi', 'Bajhang', 'Bajura','Dadeldhura', 'Darchula', 'Doti',
                'Kailali', 'Kanchanpur']
            }
        ]
        for item in d_list:
            for k, v in item.items():
                province, created = Province.objects.get_or_create(name=k)
                for x in v:
                    Districts.objects.get_or_create(province=province, name=x)
        print("Default states and districts created.")