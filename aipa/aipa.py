import logging
import requests
import json
import time
import os
import pandas as pd
import asyncio
import functools
from datetime import datetime
from .client import RestClient
from .utils import PathUtil, Singleton


class AipaRestClient(RestClient, metaclass=Singleton):
	"""
	handles auto token revoke + pure api calls
	"""
	BASE_URL = 'https://api.aipaa.ir'
	AUTH_API_URL = '/auth/token/'

	# voice
	ASR_API_URL = '/api/v1/voice/asr/'
	DIAR_API_URL = '/api/v1/voice/diar/'
	AUDIO_CLF_API_URL = '/api/v1/voice/audio-classification/'

	# vision
	SCENE_API_URL = '/api/v1/video/video-scene-detection/'
	AGE_GENDER_API_URL = '/api/v1/image/age-gender/'
	FACE_EMOTION_API_URL = '/api/v1/image/emotion/'
	FACE_VERIFICATION_URL = '/api/v1/image/face-verification/'

	# file manager
	FILE_LIST_API_URL = '/api/v1/file_manager/file/'
	DELETE_API_URL = '/api/v1/file_manager/file/'
	CLEAR_API_URL = '/api/v1/file_manager/dir/?path=./'
	UPLOAD_API_URL = '/api/v1/file_manager/file/upload/'

	AUTH_PATTERN = 'Bearer %s'

	def _call_api(self, method, api_tag, url, **kwargs):

		failure = 0
		while True:
			if 'headers' in kwargs and ('Authorization' in kwargs['headers']):
				kwargs['headers']['Authorization'] = self.AUTH_PATTERN % self.get_valid_access_token()
			response = super()._call_api(method, api_tag, url, **kwargs)
			if str(response.status_code).startswith('2'):
				return response
			else:
				failure += 1
				if failure % 3 == 0:
					time.sleep(60)

	# breakpoint()

	def __init__(self, log_path=None, name=None):
		self.client_id = 'sZof2UvI58BEMf4nTSBRAAeSoizIKoWbWcwVCffR'
		self.client_secret = 'sbPlT047wxVgIMo6p6Z6anKywdtOca4mv87KdpOZoeVzKIIi58sSgY0HXiT0HM9FTo4zyhCQGp6fFrpnSngizvG6VBswPiTOKBc5ua95Xxmo7xBUhHiL9jhqGMNlFD6q'
		self.grant_type = 'client_credentials'
		self.access_expire_time = 0
		self.access_token = None

		log_path = log_path or 'aipa_log.tsv'
		name = name or 'AIPA'
		super().__init__(log_path=log_path, name=name)

		self.user_files = []

	def set_client_info(self, client_id, client_secret):
		self.client_id = client_id
		self.client_secret = client_secret

	def revoke_access_token(self):

		payload = {'client_id': self.client_id,
		           'client_secret': self.client_secret,
		           'grant_type': self.grant_type}

		response = self._call_api('POST', 'auth', self.AUTH_API_URL,
		                          headers={}, data=payload, files=None)
		response = json.loads(response.text.encode('utf8'))

		self.access_token = response['access_token']
		self.access_expire_time = time.time() + response['expires_in']

	def get_current_access_token(self):
		return self.access_token

	def get_valid_access_token(self, valid_for_sec=60):

		if not self.get_current_access_token():
			logging.getLogger('AIPA').info(' no access token found!')
			self.revoke_access_token()
		elif time.time() + valid_for_sec > self.access_expire_time:
			logging.getLogger('AIPA').info(' access token expired!')
			self.revoke_access_token()

		return self.get_current_access_token()

	def post_asr(self, file_path, model=None):

		payload = {'model': model} if model else {}
		files = [('file', open(file_path, 'rb'))]
		headers = {'Authorization': self.AUTH_PATTERN % self.get_valid_access_token()}

		response = self._call_api('POST', f'ASR for {PathUtil.path_to_name(file_path)}', self.ASR_API_URL,
		                          headers=headers, data=payload, files=files)

		return json.loads(response.text.encode('utf8'))

	def post_diar(self, file_path):

		files = [('file', open(file_path, 'rb'))]
		headers = {'Authorization': self.AUTH_PATTERN % self.get_valid_access_token()}
		response = self._call_api('POST', f'Diarization for {PathUtil.path_to_name(file_path)}', self.DIAR_API_URL,
		                          headers=headers, data={}, files=files)
		return response

	def post_audio_clf(self, file_path):

		files = [('file', open(file_path, 'rb'))]
		headers = {'Authorization': self.AUTH_PATTERN % self.get_valid_access_token()}
		response = self._call_api('POST', f'Audio classification for {PathUtil.path_to_name(file_path)}',
		                          self.AUDIO_CLF_API_URL,
		                          headers=headers, data={}, files=files)
		return response

	def put_file(self, file_path, target_dir=None):

		files = [('file', open(file_path, 'rb'))]
		headers = {'Authorization': self.AUTH_PATTERN % self.get_valid_access_token()}
		response = self._call_api('PUT', PathUtil.path_to_name(file_path), self.UPLOAD_API_URL,
		                          headers=headers, data={}, files=files)
		return response

	def delete_file(self, file_id):

		headers = {'Authorization': self.AUTH_PATTERN % self.get_valid_access_token()}
		url = f'{self.DELETE_API_URL}{file_id}/'
		response = self._call_api('DELETE', file_id, url,
		                          headers=headers, data={}, files=[])
		return response

	def clear_files(self):

		headers = {'Authorization': self.AUTH_PATTERN % self.get_valid_access_token()}
		response = self._call_api('DELETE', 'all files', self.CLEAR_API_URL,
		                          headers=headers, data={}, files=[])
		return response

	def get_file_list(self, use_cache=True):

		if use_cache and len(self.user_files) > 0:
			return self.user_files

		headers = {'Authorization': self.AUTH_PATTERN % self.get_valid_access_token()}
		response = self._call_api('GET', 'file list', self.FILE_LIST_API_URL, headers=headers)

		file_list = json.loads(response.text.encode('utf8'))
		# file_list = file_list if isinstance(file_list, list) else []
		self.user_files = file_list
		return self.user_files

	def get_asr(self, file_id, model=None):

		headers = {'Authorization': self.AUTH_PATTERN % self.get_valid_access_token()}
		url = f'{self.ASR_API_URL}{file_id}/{model}'
		response = self._call_api('GET', f'ASR for {file_id}', url, headers=headers)

		return response

	def get_diar(self, file_id):

		headers = {'Authorization': self.AUTH_PATTERN % self.get_valid_access_token()}
		url = f'{self.DIAR_API_URL}{file_id}/'
		response = self._call_api('GET', f'Diarization for {file_id}', url, headers=headers)

		return response

	def get_audio_clf(self, file_id):

		headers = {'Authorization': self.AUTH_PATTERN % self.get_valid_access_token()}
		url = f'{self.AUDIO_CLF_API_URL}{file_id}/'
		response = self._call_api('GET', f'Audio classification for {file_id}', url, headers=headers)

		return response

	def get_scenes(self, file_id, threshold=0, min_scene_len=0, return_time=True):

		headers = {'Authorization': self.AUTH_PATTERN % self.get_valid_access_token()}
		url = f'{self.SCENE_API_URL}{file_id}/'
		data = {'return_time': return_time,
		        'threshold': threshold,
		        'min_scene_len': min_scene_len}
		response = self._call_api('POST', f'Scene Detection for {file_id}', url, headers=headers, data=data)

		return json.loads(response.text.encode('utf8'))

	def post_age_gender(self, file_path):

		payload = {'delete-file-after-process': 'y'}
		files = [('file', open(file_path, 'rb'))]
		headers = {'Authorization': self.AUTH_PATTERN % self.get_valid_access_token()}

		response = self._call_api('POST', f'AGE GENDER for {PathUtil.path_to_name(file_path)}', self.AGE_GENDER_API_URL,
		                          headers=headers, params=payload, files=files)
		return response

	def post_face_emotion(self, file_path):

		payload = {'delete-file-after-process': 'y'}
		files = [('file', open(file_path, 'rb'))]
		headers = {'Authorization': self.AUTH_PATTERN % self.get_valid_access_token()}

		response = self._call_api('POST', f'EMOTION for {PathUtil.path_to_name(file_path)}', self.AGE_GENDER_API_URL,
		                          headers=headers, params=payload, files=files)
		return response

	async def post_face_verification(self, first_file_path, second_file_path):
		params = {'delete-file-after-process': 'y'}
		files = [('first_file', open(first_file_path, 'rb')), ('second_file', open(second_file_path, 'rb'))]
		headers = {'Authorization': self.AUTH_PATTERN % self.get_valid_access_token()}
		loop = asyncio.get_event_loop()
		print(f'VERIFICATION for {PathUtil.path_to_name(first_file_path)}')
		response = await loop.run_in_executor(
			None,
			functools.partial(requests.post,
			                  url=self.BASE_URL + self.FACE_VERIFICATION_URL,
			                  headers=headers, params=params, files=files)

		)
		print(response.content)
		return response


async def main():
	logging.basicConfig(level=logging.INFO)
	client = AipaRestClient()
	client.get_valid_access_token()
	first_file_path = os.path.join('C:\\Users\\asus\\Desktop\\Arman\\race_bot\\aipa', 'ronaldo.jpg')
	second_file_path = os.path.join('C:\\Users\\asus\\Desktop\\Arman\\race_bot\\aipa', 'ronaldo2.jpg')
	third_file_path = os.path.join('C:\\Users\\asus\\Desktop\\Arman\\race_bot\\aipa', 'messi.jpg')
	await asyncio.gather(*(client.post_face_verification(first_file_path, second_file_path) for i in range(3)))


if __name__ == '__main__':

	import time

	start = time.perf_counter()
	# for i in range (5):
	# 	res = client.post_face_verification2(first_file_path, second_file_path)
	# res2 = client.post_face_verification2(first_file_path, third_file_path)
	# print(json.loads(res.content)['similarity'])
	elapsed = time.perf_counter() - start
	print(f"{__file__} executed in {elapsed:0.2f} seconds.")
	# loop = asyncio.get_event_loop()
	start2 = time.perf_counter()
	for i in range(5):
		response = asyncio.run(main())
	# response2 = asyncio.run(client.post_face_verification(first_file_path, third_file_path))
	elapsed2 = time.perf_counter() - start2
	print(f"{__file__} executed in {elapsed2:0.2f} seconds.")
# print(json.loads(response.content))
# print(json.loads(response2.content))
