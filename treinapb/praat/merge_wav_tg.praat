form
    sentence dir
endform

clearinfo

appendInfoLine: "Merging .wav and .TextGrid files..."

Create Strings as file list: "fileList", dir$ + "*.wav"
fileListPosition = selected ()
counter = Get number of strings

for i from 1 to counter
	selectObject: fileListPosition
	wav_file$ = Get string: i
	wav_filepath$ = dir$ + wav_file$
	where = index_regex (wav_file$, "_\d\d\d") - 1
	speaker$ = left$ (wav_file$, where)

	if i == 1
		begin = 1
		counter_2 = 1
		Read from file: wav_filepath$
		position = selected ()
		waves [i]  = position
		Read from file:  wav_filepath$ - ".wav" + ".TextGrid"
		position = selected ()
		tgs [i] = position
		last_speaker$ = speaker$
	elsif last_speaker$ = speaker$
		counter_2 += 1
		Read from file: wav_filepath$
		position = selected ()
		waves [i] = position
		Read from file:  wav_filepath$ - ".wav" + ".TextGrid"
		position = selected ()
		tgs [i] = position
		last_speaker$ = speaker$
	else
		for j from begin to counter_2
			plusObject: waves [j]
		endfor
		minusObject: fileListPosition
		Concatenate recoverably
		for j from begin to counter_2
			if j == begin
				selectObject: tgs [j]
			else
				plusObject: tgs [j]
			endif
		endfor
		minusObject: fileListPosition
		Concatenate
		position = selected () - 1
		plusObject: position
		Merge
		Save as text file: dir$ + last_speaker$ + ".TextGrid"
		selectObject: position - 1
		Save as WAV file: dir$ + last_speaker$ + ".wav"
		appendInfoLine: "nice"

		select all
		minusObject: fileListPosition
		Remove
		begin = i

		counter_2 += 1

		Read from file: wav_filepath$
		position = selected ()
		waves [i] = position
		Read from file:  wav_filepath$ - ".wav" + ".TextGrid"
		position = selected ()
		tgs [i] = position 
		last_speaker$ = speaker$
	endif
endfor

for j from begin to counter_2
	if j == begin
		selectObject: waves [j]
	else
		plusObject: waves [j]
	endif
endfor

minusObject: fileListPosition
Concatenate recoverably

for j from begin to counter_2
	if j == begin
		selectObject: tgs [j]
	else
		plusObject: tgs [j]
	endif
endfor

minusObject: fileListPosition
Concatenate
position = selected () - 1
plusObject: position
Merge

Save as text file: dir$ + last_speaker$ + "_Aligned.TextGrid"
selectObject: position - 1
Save as WAV file: dir$ + last_speaker$ + "_Aligned.wav"
select all
minusObject: fileListPosition
Remove

