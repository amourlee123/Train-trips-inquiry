# coding: utf-8
"""Train tickets query via command-line.

Usage:
	tickets [-gdtkz] <from> <to> <date>

Options:
	-h,--help 	显示帮助菜单
	-g 			高铁
	-d			动车
	-t			特快
	-k			特快
	-z			直达

Example:
	tickets beijing shanghai 2016-09-05
"""

#########################################
from stations import stations
from docopt import docopt
from prettytable import PrettyTable
import requests


class TrainCollection(object):

	#显示车次、出发/到达站、出发/到达时间、历时、一等座、二等座、软卧、硬卧、硬座
	header = 'train station time duration business first second softsleep hardsleep hardsit nosit'.split()
	
	def __init__(self, rows):
		self.rows = rows

	def __repr__(self):
		return '<TrainsCollection size={}>'.format(len(self))

	def __len__(self):
		return len(self.rows)
	
	def _get_duration(self, row):
		"""
		获取车次运行时间
		"""
		duration = row.get('lishi').replace(':', 'h') + 'm'
		if duration.startswith('00'):
			return duration[4:]
		if duration.startswith('0'):
			return duration[1:]
		return duration

	@property
	def trains(self):
		for row in self.rows:
			train = [
				# 车次
				row['station_train_code'],
				# 出发、到达站
				'\n'.join([row['from_station_name'], row['to_station_name']]),
				# 出发、到达时间
				'\n'.join([row['start_time'], row['arrive_time']]),
				# 历时
				self._get_duration(row),
				#商务座
				row['swz_num'],
				# 一等座
				row['zy_num'],
				# 二等座
				row['ze_num'],
				# 硬卧
				row['yw_num'],
				# 软卧
				row['rw_num'],
				# 硬座
				row['yz_num'],
				# 无座
				row['wz_num']
			]
			yield train

	def pretty_print(self):
		"""
		数据已经获取到，接下来应该提取我们要的重要信息并显示出来。
		"""
		pt = PrettyTable()
	
		# 设置每一列的标题
		if len(self) == 0:
			pt._set_field_names(['Sorry,'])
			pt.add_row([TRAIN_NOT_FOUND])
		else:
			pt._set_field_names(self.header)
			for train in self.trains:
				pt.add_row(train)
	
		print(pt)


def cli():
	arguments = docopt(__doc__)
	from_station = stations.get(arguments['<from>'])
	to_station = stations.get(arguments['<to>'])
	date = arguments['<date>']
	
	#构建URL
	url = 'https://kyfw.12306.cn/otn/lcxxcx/query?purpose_codes=ADULT&queryDate={}&from_station={}&to_station={}'.format(date, from_station, to_station)
	
	r = requests.get(url, verify=False)
	rows = r.json()['data']['datas']
	
	trains = TrainCollection(rows)
	trains.pretty_print()

#def colored(color, text):
#	table = {
#		'red': '\033[91m',
#		'green': '\033[92m',
#		'nc': "\033[0"
#	}
#
#	cv = table.get(color)
#	nc = table.get('nv')
#
#	return ''.join([cv, text, nc])



if __name__ == '__main__':
	cli() 
