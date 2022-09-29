from operator import attrgetter
import queue
import functools
import copy

class Process:
    def __init__(self, id, cpuBurst, arrTime, priority):
        self.id = id
        self.cpuBurst = cpuBurst
        self.arrTime = arrTime
        self.priority = priority
        self.waitTime = 0
        self.turTime = 0
        self.remain = cpuBurst

def AddGantt( id, time, gantt ):
    if ( time < 0 ):
        i = time
        while( i < 0 ):
            gantt.append( '-' )
            i = i + 1

    else:
        d = ''
        if ( id < 10 ):
            d = str(id)
        else:
            letter = id + 55
            d = '' + chr( letter )

        for i in range( time ):
            gantt.append( d )

def DrawGantt( fileName, gantt, method ):
    with open(fileName, 'a') as f:
        if ( method == 1 ):
            f.write('==        FCFS==\n')
        elif ( method == 2 ):
            f.write('==          RR==\n')
        elif ( method == 3 ):
            f.write('==        SRTF==\n')
        elif ( method == 4 ):
            f.write('==        PPRR==\n')
        elif ( method == 5 ):
            f.write('==        HRRN==\n')
        for i in range( len(gantt) ):
            f.write( gantt[i] )
        f.write( '\n' )

def FCFS( processList ):
    temp = []
    temp = sorted(processList, key=attrgetter('arrTime', 'id'))
    curTime = 0
    gantt = []
    for t in range( len(temp) ):
        if ( curTime < temp[t].arrTime ):
            AddGantt( temp[t].id, curTime-temp[t].arrTime, gantt )
            curTime = temp[t].arrTime
        curTime = curTime + temp[t].cpuBurst
        temp[t].turTime = curTime - temp[t].arrTime
        temp[t].waitTime = temp[t].turTime - temp[t].cpuBurst
        AddGantt( temp[t].id, temp[t].cpuBurst, gantt )

    outList = sorted(temp, key=attrgetter('id'))
    for t in range( len(outList) ):
        print(outList[t].id, outList[t].turTime, outList[t].waitTime)

    print( gantt )
    return gantt, outList

def RR( processList, timeSlice ):
    temp = []
    temp = sorted(processList, key=attrgetter('arrTime', 'id'))
    curTime = 0
    gantt = []
    terminateList = []
    readyQueue = queue.Queue()
    done = False
    readyQueue.put( temp[0] )
    i = 1
    while( done == False ):
        # running state
        work = readyQueue.get()
        if ( work.arrTime > curTime ):
            AddGantt( work.id, curTime-work.arrTime, gantt )
            curTime = work.arrTime

        if ( work.remain > timeSlice ):
            work.remain = work.remain - timeSlice
            AddGantt( work.id, timeSlice, gantt )
            curTime = curTime + timeSlice

        else:
            AddGantt( work.id, work.remain, gantt )
            curTime = curTime + work.remain
            work.remain = 0
            # terminate
            work.turTime = curTime - work.arrTime
            work.waitTime = work.turTime - work.cpuBurst
            terminateList.append( work )


        # ready state
        stop = False
        while( stop == False ):
            if ( i < len( temp ) ):
                if (temp[i].arrTime <= curTime):
                    readyQueue.put( temp[i] )
                    i = i + 1
                else:
                    stop = True

            else:
                stop = True

        if ( work.remain > 0 ):
            readyQueue.put( work )

        if ( readyQueue.empty() ):
            if ( i < len(temp) ):
                readyQueue.put( temp[i] )
                i = i + 1
            else:
                done = True
    
    outList = sorted(terminateList, key=attrgetter('id'))
    for t in range( len(outList) ):
        print(outList[t].id, outList[t].turTime, outList[t].waitTime)

    print( gantt )
    return gantt, outList
        
def SRTF( processList ):
    temp = []
    temp = sorted(processList, key=attrgetter('arrTime', 'remain', 'id'))
    curTime = 0
    gantt = []
    terminateList = []
    readyQueue = []
    done = False

    readyQueue.append( temp[0] )
    i = 1
    stop = False
    while ( stop == False ):
        if ( i < len( temp ) ):
            if ( temp[i].arrTime == temp[0].arrTime ):
                readyQueue.append( temp[i] )
                i = i + 1
            else:
                stop = True
        else:
            stop = True

    work = readyQueue[0]
    readyQueue.pop(0)
    if ( work.arrTime > curTime ):
        AddGantt( work.id, curTime-work.arrTime, gantt )
        curTime = work.arrTime

    curTime = curTime + 1
    while ( done == False ):
        work.remain = work.remain - 1
        AddGantt( work.id, 1, gantt )

        stop = False
        while ( stop == False ):
            if ( i < len(temp) ):
                if ( temp[i].arrTime == curTime ):   
                    readyQueue.append( temp[i] )
                    i = i + 1
                else:
                    stop = True
            else:
                stop = True

        if ( work.remain == 0 ):
            work.turTime = curTime - work.arrTime
            work.waitTime = work.turTime - work.cpuBurst
            terminateList.append( work )

            if ( not readyQueue ):
                if ( i < len(temp) ):
                    readyQueue.append( temp[i] )
                    i = i + 1
                    stop = False
                    while ( stop == False ):
                        if ( i < len(temp) ):
                            if ( temp[i].arrTime == readyQueue[0].arrTime ):
                                readyQueue.append( temp[i] )
                                i = i + 1
                            else:
                                stop = True
                        else:
                            stop = True
                    
                else:
                    done = True

            if ( done == False ):
                readyQueue = sorted(readyQueue, key=attrgetter('remain', 'arrTime', 'id'))
                work = readyQueue[0]
                readyQueue.pop(0)
                if ( work.arrTime > curTime ):
                    AddGantt( work.id, curTime-work.arrTime, gantt )
                    curTime = work.arrTime

        else:
            if ( readyQueue ):
                readyQueue = sorted(readyQueue, key=attrgetter('remain', 'arrTime', 'id'))
                if ( readyQueue[0].remain < work.remain ):
                    readyQueue.append( work )
                    work = readyQueue[0]
                    readyQueue.pop(0)

        curTime = curTime + 1

    outList = sorted(terminateList, key=attrgetter('id'))
    for t in range( len(outList) ):
        print(outList[t].id, outList[t].turTime, outList[t].waitTime)

    print( gantt )
    return gantt, outList

def AddPQ( readyQueue, temp ):
    a  = False
    i = 0
    while( (i < len( readyQueue )) and ( a == False ) ):
        if ( temp.priority < readyQueue[i].priority ):
            readyQueue.insert( i, temp )
            a = True

        i = i + 1

    if ( a == False ):
        readyQueue.append( temp )

def PPRR( processList, timeSlice ):
    temp = []
    temp = sorted(processList, key=attrgetter('arrTime', 'priority', 'id'))
    curTime = 0
    gantt = []
    terminateList = []
    readyQueue = []
    done = False
    timer = 0
    readyQueue.append( temp[0] )
    i = 1
    stop = False
    while ( stop == False ):
        if ( i < len( temp ) ):
            if ( temp[i].arrTime == temp[0].arrTime ):
                readyQueue.append( temp[i] )
                i = i + 1
            else:
                stop = True
        else:
            stop = True

    work = readyQueue[0]
    readyQueue.pop(0)
    if ( work.arrTime > curTime ):
        AddGantt( work.id, curTime-work.arrTime, gantt )
        curTime = work.arrTime

    curTime = curTime + 1
    while ( done == False ):
        work.remain = work.remain - 1
        AddGantt( work.id, 1, gantt )
        timer = timer + 1

        stop = False
        while ( stop == False ):
            if ( i < len(temp) ):
                if ( temp[i].arrTime == curTime ):   
                    AddPQ( readyQueue, temp[i] )
                    i = i + 1
                else:
                    stop = True
            else:
                stop = True

        if ( work.remain == 0 ):
            work.turTime = curTime - work.arrTime
            work.waitTime = work.turTime - work.cpuBurst
            terminateList.append( work )

            if ( not readyQueue ):
                if ( i < len(temp) ):
                    readyQueue.append( temp[i] )
                    i = i + 1
                    stop = False
                    while ( stop == False ):
                        if ( i < len(temp) ):
                            if ( temp[i].arrTime == readyQueue[0].arrTime ):
                                readyQueue.append( temp[i] )
                                i = i + 1
                            else:
                                stop = True
                        else:
                            stop = True
                    
                else:
                    done = True

            if ( done == False ):
                work = readyQueue[0]
                readyQueue.pop(0)
                timer = 0
                if ( work.arrTime > curTime ):
                    AddGantt( work.id, curTime-work.arrTime, gantt )
                    curTime = work.arrTime

        elif ( readyQueue ):
            if ( work.priority > readyQueue[0].priority ):
                AddPQ( readyQueue, work )
                work = readyQueue[0]
                readyQueue.pop(0)
                timer = 0

            elif( timer == timeSlice ):
                timer = 0
                if ( work.priority == readyQueue[0].priority ):
                    AddPQ( readyQueue, work )
                    work = readyQueue[0]
                    readyQueue.pop(0)

        curTime = curTime + 1

    outList = sorted(terminateList, key=attrgetter('id'))
    for t in range( len(outList) ):
        print(outList[t].id, outList[t].turTime, outList[t].waitTime)

    print( gantt )
    return gantt, outList

def compare( p1, p2 ):
    if ( p1.priority > p2.priority ):
        return 1
    elif ( p1.priority == p2.priority ):
        if ( p1.arrTime < p2.arrTime ):
            return 1
        elif ( p1.arrTime == p2.arrTime ):
            if ( p1.id < p2.id ):
                return 1
            else:
                return -1
        else:
            return -1
    else:
        return -1

def HRRN( processList ):
    temp = []
    temp = sorted(processList, key=attrgetter('arrTime', 'id'))
    curTime = 0
    gantt = []
    readyQueue = []
    terminateList = []
    done = False
    readyQueue.append( temp[0] )
    i = 1
    while( done == False ):
        # running state
        work = readyQueue[0]
        readyQueue.pop(0)

        if ( work.arrTime > curTime ):
            AddGantt( work.id, curTime-work.arrTime, gantt )
            curTime = work.arrTime

        AddGantt( work.id, work.cpuBurst, gantt )
        curTime = curTime + work.cpuBurst

        # terminate
        work.turTime = curTime - work.arrTime
        work.waitTime = work.turTime - work.cpuBurst
        terminateList.append( work )

        # ready state
        stop = False
        while( stop == False ):
            if ( i < len( temp ) ):
                if (temp[i].arrTime <= curTime):
                    readyQueue.append( temp[i] )
                    i = i + 1
                else:
                    stop = True

            else:
                stop = True

        for j in range( len(readyQueue) ):
            readyQueue[j].priority = (( curTime - readyQueue[j].arrTime ) + readyQueue[j].cpuBurst ) / readyQueue[j].cpuBurst

        readyQueue = sorted(readyQueue, reverse=True, key=functools.cmp_to_key(compare))

        if ( not readyQueue ):
            if ( i < len(temp) ):
                readyQueue.append( temp[i] )
                i = i + 1
            else:
                done = True

    outList = sorted(terminateList, key=attrgetter('id'))
    for t in range( len(outList) ):
        print(outList[t].id, outList[t].turTime, outList[t].waitTime)

    print( gantt )
    return gantt, outList

def PrintM( fileName, outList, methodName ):
    with open(fileName, 'a') as f:
        f.write( '===========================================================\n\n' )
        f.write( 'Waiting Time\n' )
        f.write( 'ID\t' )
        f.write( methodName )
        f.write( '\n' )
        f.write( '===========================================================\n' )
        for i in range( len(outList) ):
            f.write( str(outList[i].id) )
            f.write( '\t' )
            f.write( str(outList[i].waitTime) )
            f.write( '\n' )
        f.write( '===========================================================\n\n' )
        f.write( 'Turnaround Time\n' )
        f.write( 'ID\t' )
        f.write( methodName )
        f.write( '\n' )
        f.write( '===========================================================\n' )
        for j in range( len(outList) ):
            f.write( str(outList[j].id) )
            f.write( '\t' )
            f.write( str(outList[j].turTime) )
            f.write( '\n' )
        f.write( '===========================================================\n\n' )

def Method1( name, processList ):
    fileName = "out_" + name + ".txt"
    with open(fileName, 'w') as f:
        f.write( 'FCFS\n' )

    gantt, outList = FCFS( processList )
    DrawGantt( fileName, gantt, 1 )
    PrintM( fileName, outList, 'FCFS' )

def Method2( name, processList, timeSlice ):
    fileName = "out_" + name + ".txt"
    with open(fileName, 'w') as f:
        f.write( 'RR\n' )

    gantt, outList = RR( processList, timeSlice )
    DrawGantt( fileName, gantt, 2 )
    PrintM( fileName, outList, 'RR' )

def Method3( name, processList ):
    fileName = "out_" + name + ".txt"
    with open(fileName, 'w') as f:
        f.write( 'SRTF\n' )

    gantt, outList = SRTF( processList )
    DrawGantt( fileName, gantt, 3 )
    PrintM( fileName, outList, 'SRTF' )

def Method4( name, processList, timeSlice ):
    fileName = "out_" + name + ".txt"
    with open(fileName, 'w') as f:
        f.write( 'Priority RR\n' )

    gantt, outList = PPRR( processList, timeSlice )
    DrawGantt( fileName, gantt, 4 )
    PrintM( fileName, outList, 'PPRR' )

def Method5( name, processList ):
    fileName = "out_" + name + ".txt"
    with open(fileName, 'w') as f:
        f.write( 'HRRN\n' )

    gantt, outList = HRRN( processList )
    DrawGantt( fileName, gantt, 5 )
    PrintM( fileName, outList, 'HRRN' )

def Method6( name, processList, timeSlice ):
    fileName = "out_" + name + ".txt"
    with open(fileName, 'w') as f:
        f.write( 'All\n' )

    processList1 = copy.deepcopy(processList)
    processList2 = copy.deepcopy(processList)
    processList3 = copy.deepcopy(processList)
    processList4 = copy.deepcopy(processList)
    processList5 = copy.deepcopy(processList)

    gantt1, outList1 = FCFS( processList1 )
    DrawGantt( fileName, gantt1, 1 )
    gantt2, outList2 = RR( processList2, timeSlice )
    DrawGantt( fileName, gantt2, 2 )
    gantt3, outList3 = SRTF( processList3 )
    DrawGantt( fileName, gantt3, 3 )
    gantt4, outList4 = PPRR( processList4, timeSlice )
    DrawGantt( fileName, gantt4, 4 )
    gantt5, outList5 = HRRN( processList5 )
    DrawGantt( fileName, gantt5, 5 )

    with open(fileName, 'a') as f:
        f.write( '===========================================================\n\n' )
        f.write( 'Waiting Time\n' )
        f.write( 'ID\tFCFS\tRR\tSRTF\tPPRR\tHRRN\n' )
        f.write( '===========================================================\n' )
        for i in range( len(outList1) ):
            f.write( str(outList1[i].id) )
            f.write( '\t' )
            f.write( str(outList1[i].waitTime) )
            f.write( '\t' )
            f.write( str(outList2[i].waitTime) )
            f.write( '\t' )
            f.write( str(outList3[i].waitTime) )
            f.write( '\t' )
            f.write( str(outList4[i].waitTime) )
            f.write( '\t' )
            f.write( str(outList5[i].waitTime) )
            f.write( '\n' )
        f.write( '===========================================================\n\n' )
        f.write( 'Turnaround Time\n' )
        f.write( 'ID\tFCFS\tRR\tSRTF\tPPRR\tHRRN\n' )
        f.write( '===========================================================\n' )
        for j in range( len(outList1) ):
            f.write( str(outList1[j].id) )
            f.write( '\t' )
            f.write( str(outList1[j].turTime) )
            f.write( '\t' )
            f.write( str(outList2[j].turTime) )
            f.write( '\t' )
            f.write( str(outList3[j].turTime) )
            f.write( '\t' )
            f.write( str(outList4[j].turTime) )
            f.write( '\t' )
            f.write( str(outList5[j].turTime) )
            f.write( '\n' )
        f.write( '===========================================================\n\n' )

if __name__ == '__main__':
    keep = True
    while keep:
        fileName = input( "請輸入檔案名稱:\n" )
        name = fileName + ".txt"
        f = None
        processList = []
        method = 0
        timeSlice = -1
        try:
            f = open(name, 'r')
            first_line = f.readline()
            op = first_line.split()
            method = int(op[0])
            print(method)
            timeSlice = int(op[1])
            print( timeSlice )
            second_line = f.readline()
            for line in f.readlines():
                num = line.split(  )
                if num:
                    if not num[0] == '':
                        item = Process( int(num[0]), int(num[1]), int(num[2]), int(num[3]) )
                        processList.append( item )
        
            if ( method == 1 ):
                Method1( fileName, processList )
            elif ( method == 2 ):
                Method2( fileName, processList, timeSlice )
            elif ( method == 3 ):
                Method3( fileName, processList )
            elif ( method == 4 ):
                Method4( fileName, processList, timeSlice )
            elif ( method == 5 ):
                Method5( fileName, processList )
            elif ( method == 6 ):
                Method6( fileName, processList, timeSlice )

        except IOError:
            print('ERROR: can not found ' + name)
            if f:
                f.close()
        finally:
            if f:
                f.close()

        processList.clear()
        cmd = input( "繼續請輸入1\n" )
        if cmd == "1":
            keep = True

        else:
            keep = False