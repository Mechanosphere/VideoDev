import schedule
import time
from controller import WorkFlowControllerStage1
from controller import WorkFlowControllerStage2


def schedule_stage1():
    print('starting work flow stage 1: check for new jobs')
    x = WorkFlowControllerStage1()
    print(x.new_job())
    print('sleeping for 5 seconds')
    time.sleep(5)
    print('starting work flow stage 1: adding media')
    print(x.add_images_to_id())
    time.sleep(5)
    print('checking db to look for images to encode')
    print('starting work flow stage 2: check for ready_for_image_encode')
    y = WorkFlowControllerStage2()
    print(y.process_new_jobs())
    print('sleeping for 5 seconds')
    time.sleep(35)
    print('starting work flow stage 2: processing video list')
    print(y.process_video_list())
    time.sleep(35)
    print('starting work flow stage 2: processing concat video list')
    print(y.process_concat_video_list())
    print('Finished work flow stage 2')
    print('Sleeping for 50 seconds')
    time.sleep(50)



schedule.every(5).seconds.do(schedule_stage1)




while True:
    schedule.run_pending()
    time.sleep(1)