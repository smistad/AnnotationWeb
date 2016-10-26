from common.exporter import Exporter
from common.metaimage import MetaImage
from common.utility import create_folder, copy_image
from annotationweb.models import ProcessedImage, Dataset, Task, Label, Subject
from boundingbox.models import BoundingBox
from django import forms
import os
from os.path import join
from shutil import rmtree, copyfile


class BoundingBoxExporterForm(forms.Form):
    path = forms.CharField(label='Storage path', max_length=1000)
    delete_existing_data = forms.BooleanField(label='Delete any existing data at storage path', initial=False, required=False)

    def __init__(self, task, data=None):
        super().__init__(data)
        self.fields['subjects_training'] = forms.ModelMultipleChoiceField(
            queryset=Subject.objects.filter(dataset__task=task))
        self.fields['subjects_validation'] = forms.ModelMultipleChoiceField(
            queryset=Subject.objects.filter(dataset__task=task))


class BoundingBoxExporter(Exporter):
    """
    asdads
    """

    task_type = Task.BOUNDING_BOX
    name = 'Default bounding box exporter'

    def get_form(self, data=None):
        return BoundingBoxExporterForm(self.task, data=data)

    def export(self, form):
        delete_existing_data = form.cleaned_data['delete_existing_data']
        # Create dir, delete old if it exists
        path = form.cleaned_data['path']
        if delete_existing_data:
            # Delete path
            try:
                os.stat(path)
                rmtree(path)
            except:
                # Folder does not exist
                pass

        # Create folder if it doesn't exist
        create_folder(path)
        try:
            os.stat(path)
        except:
            return False, 'Failed to create directory at ' + path

        # Create training folder
        training_path = join(path, 'training')
        create_folder(training_path)
        validation_path = join(path, 'validation')
        create_folder(validation_path)

        # TODO check that training and validation subjects are not overlapping

        self.add_subjects_to_path(training_path, form.cleaned_data['subjects_training'])
        self.add_subjects_to_path(validation_path, form.cleaned_data['subjects_validation'])

        return True, path

    def add_subjects_to_path(self, path, data):

        # Get labels for this task and write it to labels.txt
        label_file = open(join(path, 'labels.txt'), 'w')
        labels = Label.objects.filter(task=self.task)
        label_dict = {}
        counter = 0
        for label in labels:
            label_file.write(label.name + '\n')
            label_dict[label.id] = counter
            counter += 1
        label_file.close()

        images = ProcessedImage.objects.filter(task=self.task, image__subject__in=data)
        for image in images:
            name = image.image.filename
            image_filename = name[name.rfind('/')+1:]
            create_folder(join(path, 'images'))
            create_folder(join(path, 'labels'))

            # Copy image to images folder
            image_id = image.image.pk
            new_filename = join(path, join('images', str(image_id) + '.png'))
            copy_image(name, new_filename)

            # Write bounding boxes to labels folder
            # TODO write label for each bounding box
            boxes = BoundingBox.objects.filter(image=image)
            with open(join(path, join('labels', str(image_id) + '.txt')), 'w') as f:
                for box in boxes:
                    center_x = round(box.x + box.width*0.5)
                    center_y = round(box.y + box.height*0.5)
                    label = label_dict[box.label.id]
                    f.write('{} {} {} {} {}\n'.format(label, center_x, center_y, box.width, box.height))

        return True, path

