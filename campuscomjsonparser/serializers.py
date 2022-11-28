import json
from rich import print


class ProductSerializer():
    def __init__(self, mapping, data):
        self.mapping = mapping
        self.data = data

    def serialize(self):
        product_dict = json.loads(self.data)
        product = {}

        for key, val in self.mapping.get('product', {}).items():
            if key == 'skills':
                product[key] = []

                if product_dict.get(val, []) is None:
                    product[key].append({})
                else:
                    for skill in product_dict.get(val, []):
                        skill_serializer = SkillSerializer(self.mapping, skill)
                        product[key].append(skill_serializer.serialize())

            elif key == 'topics':
                product[key] = []
                for topic in product_dict.get(val, []):
                    topic_serializer = TopicSerializer(self.mapping, topic)
                    product[key].append(topic_serializer.serialize())

            elif key == 'modules':
                product[key] = []
                for module in product_dict.get(val, []):
                    module_serializer = ModuleSerializer(self.mapping, module)
                    product[key].append(module_serializer.serialize())

            elif key == 'prerequisites':
                product[key] = ','.join(product_dict.get(val, []))

            elif key == 'total_enrolled':
                try:
                    product[key] = int(product_dict.get(val, None).replace(',', ''))
                except ValueError:
                    product[key] = None
                except AttributeError:
                    product[key] = None

            else:
                try:
                    product[key] = product_dict.get(val, None)
                except TypeError:
                    import ipdb; ipdb.set_trace()
        return product


class SkillSerializer():
    def __init__(self, mapping, data):
        self.mapping = mapping
        self.data = data

    def serialize(self):
        skill = {}

        for key, val in self.mapping.get('skill', {}).items():
            skill[key] = self.data.get(val, None)

        return skill


class TopicSerializer():
    def __init__(self, mapping, data):
        self.mapping = mapping
        self.data = data

    def serialize(self):
        topic = {}

        for key, val in self.mapping.get('topic', {}).items():
            topic[key] = self.data.get(val, None)

        return topic


class ModuleSerializer():
    def __init__(self, mapping, data):
        self.mapping = mapping
        self.data = data

    def serialize(self):
        module = {}

        for key, val in self.mapping.get('module', {}).items():
            if key == 'lessons':
                module[key] = []
                for lesson in self.data.get(val, []):
                    lesson_serializer = LessonSerializer(self.mapping, lesson)
                    module[key].append(lesson_serializer.serialize())
            else:
                module[key] = self.data.get(val, None)

        return module


class LessonSerializer():
    def __init__(self, mapping, data):
        self.mapping = mapping
        self.data = data

    def serialize(self):
        lesson = {}

        for key, val in self.mapping.get('lesson', {}).items():
            lesson[key] = self.data.get(val, None)

        return lesson
