"""Увага: не використовувати counting_sort для чисел більше 1 мільйона, використовувати radix_sort"""

def counting_sort(ns, nsout=[]):
	intermediates_1=max(ns)+1
	intermediates_2=[0]*intermediates_1
	for n in ns:
		intermediates_2[n]+=1
	for x in range(1, intermediates_1):
		intermediates_2[x]+=intermediates_2[x-1]
	outns=[0]*len(ns)
	for x in range(len(ns)-1, -1, -1):
		if nsout!=[]:
			outns[intermediates_2[ns[x]]-1]=nsout[x]
		else:
			outns[intermediates_2[ns[x]]-1]=ns[x]
		intermediates_2[ns[x]]-=1
	return outns
def digit_sort(ns, dg):
	out=[]
	mx=max(len(str(n)) for n in ns)
	for n in ns:
		nstrrep=str(n)[::-1]
		if dg>=mx:
			out.append(0)
		elif dg<len(nstrrep):
			out.append(int(nstrrep[dg]))
		else:
			out.append(0)
	return out
def sign_sort(ns):
	negn=[]
	posn=[]
	zeros=[]
	for x in range(0, len(ns)):
		if str(ns[x])[0]=="-":
			negn.append(int(str(ns[x])[1:]))
		elif ns[x]==0:
			zeros.append(0)
		else:
			posn.append(ns[x])
	return negn, zeros, posn
def add_neg(ns):
	negs=[]
	for n in ns:
		negs.append(-n)
	return negs
def radix_sort(ns, patch=True):
	if ns==[]:
		return []
	temp=ns
	if patch:
		n,z,p=sign_sort(ns)
		nsort=radix_sort(n, False)
		psort=radix_sort(p, False)
		nsort.reverse()
		nsort=add_neg(nsort)
		nsort.extend(z)
		nsort.extend(psort)
		results=[]
		for n in range(len(nsort)):
			results.append(ns.index(nsort[n]))
		return nsort, results
	for x in range(0, max(len(str(n)) for n in ns)):
		dgts=digit_sort(temp, x)
		temp=counting_sort(dgts, temp)
	return temp
def bubble_sort(ns):
	for x in range(0, len(ns)):
			for y in range(0, len(ns)-x-1):
				if ns[y+1]<ns[y]:
					ns[y+1], ns[y]=ns[y], ns[y+1]
	return ns
def mini(ns, froma):
	nsact=ns[froma:]
	ind=0
	for x in range(0, len(nsact)):
		if nsact[x]<nsact[ind]:
			ind=x
	return ind+froma
def selection_sort(ns):
	for x in range(0, len(ns)):
		mi=mini(ns, x)
		ns[x], ns[mi]=ns[mi], ns[x]
	return ns
def insertion_sort(ns):
	for x in range(1, len(ns)):
		k=ns[x]
		y=x-1
		while y>=0 and k<ns[y]:
			ns[y+1]=ns[y]
			y-=1
		ns[y+1]=k
	return ns
def partit(ns, l, h):
	piv=ns[h]
	x=l-1
	for y in range(l, h):
		if ns[y]<piv:
			x+=1
			ns[x], ns[y]=ns[y], ns[x]
	ns[x+1], ns[h]=ns[h], ns[x+1]
	return x+1
def quick_sort(ns, l="", h=""):
	if l=="":
		l=0
		h=len(ns)-1
	if l>=h:
		return
	pi=partit(ns, l, h)
	quick_sort(ns, l, pi-1)
	quick_sort(ns, pi+1, h)
	return ns
def is_sorted(ns):
	val=True
	pv=ns[0]
	for n in ns[1:]:
		if n<pv:
			val=False
			break
		pv=n
	return val
def adv_bubble_sort(ns):
	k=ns.copy()
	k.reverse()
	if is_sorted(k):
		return k
	for x in range(0, len(ns)):
		issw=False
		for y in range(0, len(ns)-x-1):
				if ns[y+1]<ns[y]:
					ns[y+1], ns[y]=ns[y], ns[y+1]
					issw=True
		if not issw:
			break
	return ns
