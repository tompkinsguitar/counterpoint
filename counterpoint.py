'''
    Author: Daniel C. Tompkins
    Email: tompkinsguitar@gmail.com
    
    Please feel free to use this as you wish, and I welcome any feedback.
'''


import random, copy
from timeit import timeit
from music21 import *


class CounterPoint:
    perfect_intervals = (0, 7, 12)
    illegal_intervals = (1, 2, 5, 6, 10, 11)
    thirds = (3, 4)
    sixths = (8, 9)

    diatonic_pcs = (0, 2, 4, 5, 7, 9, 11)
    chromatic_pcs = (1, 3, 6, 8, 10)

    illegal_skips = range(9, 12)


    pc_modes = {
        'ionian': (0, (11, 2)),
        'dorian': (2, (1, 4)),
        'phrygian': (4, (2, 5)),
        'lydian': (5, (4, 7)),
        'mixolydian': (7, (6, 9)),
        'aeolian': (9, (8, 11))
    }

    clefs = {'treble': range(57, 79), 'bass': range(45, 64)}

    # def __init__(self, mode='ionian', length=6, clef='treble'):
    #     self.mode = mode
    #     self.length = length
    #     self.clef = clef

    def melody_maker(self, clef='treble', length=6, mode='ionian',
                     zenith_threshold=1, nadir_threshold=1):
        # clef = self.clef
        # length = self.length
        # mode = self.mode
        '''find all possible notes'''
        mel = [0 for x in range(length)]
        possible_notes = []
        possible_cadences = []
        for x in self.clefs[clef]:
            if x%12 in self.diatonic_pcs:
                possible_notes.append(x)
            if x%12 in self.pc_modes[mode][1]:
                possible_cadences.append(x)
        possible_notes = random.sample(possible_notes, len(possible_notes))

        '''make the cadence'''
        possible_cadences = random.sample(possible_cadences, len(possible_cadences))
        possible_final = []
        possible_penultimate = []
        for x in possible_notes:
            if x%12 == self.pc_modes[mode][0]:
                possible_final.append(x)
        thefinal = random.choice(possible_final)
        mel[0] = thefinal
        mel[-1] = thefinal
        for x in possible_cadences:
            if abs(x-thefinal) <= 4:
                possible_penultimate.append(x)
        mel[-2] = random.choice(possible_penultimate)

        for n in range(1, len(mel[:-2])):
            next_note = []
            for nn in possible_notes:
                if nn != mel[n-1]: #no repeated notes
                    if abs(nn - mel[n-1]) not in self.illegal_skips: #no illegal skips
                        if n == len(mel[1:-2]):
                            if mel[-2] in self.chromatic_pcs: #check for augmented second
                                if mel[-2] - nn < 3: #and leap into chromatic note
                                    next_note.append(nn)
                            elif abs(mel[-2] - nn) <= 4:
                                next_note.append(nn)
                        else:
                            next_note.append(nn)
            mel[n]=random.choice(next_note)
        #test_mel = self.check_melody(mel=mel, mode=mode,
        #                             zenith_threshold=zenith_threshold,
        #                             nadir_threshold=nadir_threshold)
        return mel


    def check_melody(self, mel, mode='ionian', zenith_threshold=1, nadir_threshold=1):
        if mel[0] != mel[-1]:
            print('it was the first and last note')
            return False
        elif mel[-2]%12 not in self.pc_modes[mode][-1]:
            print('penultimate')
            return False
        for x in range(1, len(mel)):
            if mel[x - 1] == mel[x]:
                print('consecutive', mel[x-1], mel[x])
                return False

            interval = abs(mel[x] - mel[x - 1])


            if interval in range(10, 12) or interval > 12:
                print('leap too big', mel[x], mel[x-1], interval)
                return False
            elif interval == 6:
                print('tritone')
                return False
            elif mel[x] % 12 not in self.diatonic_pcs and mel[x] - mel[x - 1] == 3:
                # print(mel[x]%12, mel[x-1]%12, mel[x] - mel[x-1])
                print('augmented second')
                return False
            elif mel[x] % 12 not in self.diatonic_pcs and abs(mel[x] - mel[x - 1]) % 12 > 4:
                print('leap into dissonance', mel[x] % 12, mel[x - 1] % 12, abs(mel[x] - mel[x - 1]) % 12)
                return False
            elif x != len(mel):
                if interval > 4 and abs(mel[x+1] - mel[x]) > 4:
                    print('too leap-y')
                    return False
        zenith = 0
        nadir = 0
        for x in mel[1:-1]:
            if x == max(mel):
                zenith += 1
            elif x == min(mel):
                nadir += 1
        if nadir > nadir_threshold:
            print('it was the nadir', min(mel), nadir)
            return False
        if zenith > zenith_threshold:
            print('it was the zenith', max(mel), zenith)
            return False
        # self.melody.append(mel)
        return True

    def counterpoint_checker(self, cf, cpt):
        all_intervals = []
        for n in range(len(cpt) - 1):
            interval = cpt[n] - cf[n]
            all_intervals.append(interval)
            p_interval = cpt[n + 1] - cf[n + 1]
            if interval >= 20 or interval < 0:  # range issues
                print('range issues', interval)
                return False
            elif interval % 12 in self.illegal_intervals:  # illegal harmonic interval
                print('illegal interval', interval, interval % 12)
                return False
            elif interval == 7 and p_interval == 7:  # parallel fifths
                print('consecutive fifths', interval, p_interval)
                return False
            elif p_interval in self.perfect_intervals and cpt[n] - cpt[n - 1] > 2 and cf[n] - cf[n - 1] > 2:
                print('direct perfects')
                return False
            elif p_interval in self.perfect_intervals and cpt[n - 1] - cpt[n] > 2 and cf[n - 1] - cf[n] > 2:
                print('direct perfects')
                return False
        print('checking thirds')
        thirds_counter = 0
        sixths_counter = 0
        for n in range(len(cpt)):
            interval = (cpt[n] - cf[n]) % 12
            if interval in self.thirds:
                thirds_counter += 1
                if thirds_counter >= 4:
                    print('too many thirds')
                    return False
            else:
                thirds_counter = 0
            if interval in self.sixths:
                sixths_counter += 1
                if sixths_counter >= 4:
                    print('too many sixths')
                    return False
            else:
                sixths_counter = 0
        upward_motion = 0
        downward_motion = 0
        for n in range(1, len(cpt)):
            if cpt[n] > cpt[n - 1] and cf[n] > cf[n - 1]:  # no contrary motion
                upward_motion += 1
                downward_motion = 0
            if upward_motion > 3:
                print('upward motion')
                return False
            elif cpt[n] < cpt[n - 1] and cf[n] < cf[n - 1]:
                upward_motion = 0
                downward_motion += 1
            if downward_motion > 3:
                print('downward motion')
                return False
        for n in range(1, len(cpt)):  # leap in same direction
            if cpt[n - 1] - cpt[n] > 3 and cf[n - 1] - cf[n] > 3:
                print('leap same direction')
                return False
            elif cpt[n] - cpt[n - 1] > 3 and cf[n] - cf[n - 1] > 3:
                print('leap same direction')
                return False
        if abs(cf[-2] - cf[-1]) > 2 and abs(cpt[-2] - cpt[-1]) > 2:  # cadence
            print('cadence intervals')
            return False
        elif abs(cf[-2] - cf[-1]) > 7 or abs(cpt[-2] - cpt[-1]) > 7:
            print('cadence intervals')
            return False
        elif cf[-2] % 12 in self.chromatic_pcs and cpt[-3] % 12 == cf[-2] % 12 - 1:  # cross relations
            print('cross relation')
            return False
        elif cpt[-2] % 12 in self.chromatic_pcs and cf[-3] % 12 == cpt[-2] % 12 - 1:
            print('cross relation')
            return False
        elif cf[-2] % 12 in self.chromatic_pcs and cf[-3] % 12 == cf[-2] % 12 - 1:  # cross relations
            print('cross relation')
            return False
        elif cpt[-2] % 12 in self.chromatic_pcs and cpt[-3] % 12 == cpt[-2] % 12 - 1:
            print('cross relation')
            return False
        for a, b in zip(cf[1:-1], cpt[1:-1]):
            if abs(a - b) % 12 == 0:
                print('octave in middle')
                return False
        return True

    def make_counterpoint(self, length=6, mode='ionian',
                          cf_clef='bass', cpt_clef='treble',
                          nadir_threshold=1, zenith_threshold=1):
        cpt = self.melody_maker(length=length, mode=mode, clef=cpt_clef,
                                zenith_threshold=zenith_threshold,
                                nadir_threshold=nadir_threshold)
        cf = self.melody_maker(length=length, mode=mode, clef=cf_clef,
                               zenith_threshold=zenith_threshold,
                               nadir_threshold=nadir_threshold)
        if len(cf) != len(cpt):
            raise ValueError('Cantus and Counterpoint melodies must be the same length')
        trial_counterpoint = self.counterpoint_checker(cf=cf, cpt=cpt)
        cf_trial = 0
        while trial_counterpoint is False:
            cf_trial += 1
            
            if cf_trial == 200:
                zenith_threshold += 1
                nadir_threshold += 1
            elif cf_trial == 400:
                zenith_threshold += 1
                nadir_threshold += 1
            elif cf_trial == 600:
                zenith_threshold += 1
                nadir_threshold += 1
            elif cf_trial == 800:
                zenith_threshold += 1
                nadir_threshold += 1
            cpt = self.melody_maker(length=length, mode=mode, clef=cpt_clef, nadir_threshold=nadir_threshold,
                                    zenith_threshold=zenith_threshold)
            if cf_trial == 999:
                print('trying new cf()()()()()()()()()()()()()()()()()()()()()()()')
                cf = self.melody_maker(length=length, mode=mode, clef=cf_clef, nadir_threshold=nadir_threshold,
                                       zenith_threshold=zenith_threshold)
                cf_trial = 0
                zenith_threshold = 1
                nadir_threshold = 1
            trial_counterpoint = self.counterpoint_checker(cf=cf, cpt=cpt)
        return {'counterpoint': cpt, 'cantus': cf}


if __name__ == '__main__':

    from time import time

    st = time()

    #This ensures leading tones with sharps rather than enharmonic spellings
    notes = {0: 'C', 1: 'C#', 2: 'D', 3: 'D#', 4: 'E', 5: 'F', 6: 'F#', 7: 'G', 8: 'G#', 9: 'A', 10: 'B-', 11: 'B'}
    octaves = {'2': [x for x in range(36, 36+12)],
               '3': [x for x in range(48, 48 + 12)],
               '4': [x for x in range(60, 60 + 12)],
               '5': [x for x in range(72, 72 + 12)]}

    C = CounterPoint()


    cantus = stream.Part(id='cantus')
    counterpoint = stream.Part(id='counterpoint')
    C = CounterPoint()



    '''
    this is where you input what parameters you want
    WARNING: at this time, if length > 9, it takes a long time to finish
    '''
    final_cpt = C.make_counterpoint(mode='phrygian', cf_clef='bass', cpt_clef='treble',
                                    length=6, zenith_threshold=1, nadir_threshold=1)

    '''
    This puts everything on a score. If there is an error, make sure you 
    have music21's environment settings pointed to your notation software.
    I recommend musescore. Music21 tries to find the software, but if there is an error:
    
    in python, type:
    from music21 import *
    us = environment.UserSettings()
    us.create() #you might not have to do this
    us['musicxmlPath'] = '/Applications/MuseScore 2.app'
    '''

    print(final_cpt['counterpoint'], 'counterpoint')
    print(final_cpt['cantus'], 'cantus')
    for x in final_cpt['cantus']:  # cf
        c_note = notes[x % 12]
        c_octave = ''
        for a, b in octaves.items():
            if x in b:
                c_octave = a
        cantus.append(note.Note(c_note + c_octave, type='whole'))

    for x in final_cpt['counterpoint']:  # ctpt
        c_note = notes[x % 12]
        c_octave = ''
        for a, b in octaves.items():
            if x in b:
                c_octave = a
        counterpoint.append(note.Note(c_note + c_octave, type='whole'))

    S = stream.Score()
    S.insert(counterpoint)
    S.insert(cantus)
    print('finished in', time() - st, 'seconds')
    S.show()

