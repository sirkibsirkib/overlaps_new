from Bio import SeqIO
def rd(filename):
	fasta_sequences = SeqIO.parse(open(filename), 'fasta')
	return {fasta.id:str(fasta.seq) for fasta in fasta_sequences}
