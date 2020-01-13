import lz4.frame
import os

def lz4_compression(data, dbPk, outputDir):
    outputName = str(dbPk) + '_compressed'
    output_path = os.path.join(outputDir, outputName)
    out = open(output_path, 'wb')
    input_data = bytes(data, 'utf-8')
    compressed_data = lz4.frame.compress(input_data, compression_level=3) #压缩比0-16可调，level越大时间越长
    out.write(compressed_data)

    return output_path

def lz4_decompression(input_path):
    f = open(input_path,'rb')
    input_data = f.read()
    decompressed_data = lz4.frame.decompress(input_data)
    decompressed_data = str(decompressed_data,'utf-8')
    decompressed_data = decompressed_data.replace('\r','')
    decompressed_data = decompressed_data.replace('\n',' ')
    #print("decompressed_data:{}".format(decompressed_data[-10:]))
    bins_and_freq = decompressed_data.split(" ")
    #print("bins_and_freq:{}".format(bins_and_freq[-10:]))
    half_length = round(0.5*len(bins_and_freq))
    bins = [float(s) for s in bins_and_freq[:half_length]]
    freq = [float(s) for s in bins_and_freq[half_length:]]
    # bins = bins_and_freq[:half_length]
    # freq = bins_and_freq[half_length:]

    return bins, freq


