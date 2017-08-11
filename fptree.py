

import itertools

class FPTreeNode(object):
    """
        FPTree Node structure
    """
    def __init__(self, item, count, parent):
        self.item = item
        self.count = count
        self.parent = parent
        self.link = None
        self.children = []

    def get_child(self, item):
        for child in self.children:
            if (child.item == item):
                return child
        return None

    def add_child(self, item):
        newNode = FPTreeNode(item,1,self)
        self.children.append(newNode)
        return newNode

class FPTree(object):

    def __init__(self,transactions, min_support,root_count,root_value):
        self.transactions=transactions
        self.min_support = min_support
        self.frequent_itemsets=self.get_frequent_items(transactions,min_support)
        self.headers=self.set_headers(self.frequent_itemsets)
        self.root=FPTreeNode(root_value,root_count,None)

    def set_headers(self,frequent_itemsets):
        headers={}
        for item in frequent_itemsets:
            headers[item]=None
        return headers

    def get_frequent_items(self,transactions,min_support):
        items={}
        for transaction in transactions:
            for item in transaction:
                if item in items:
                    items[item]+=1
                else:
                    items[item]=1

        for key in list(items.keys()):
            if items[key] < min_support:
                del items[key]

       # print("Frequent items ",items)
        return items

    def build_tree(self):
        for tran in self.transactions:
            unsorted_items=[]
            for item in tran:
                if item in self.frequent_itemsets:
                    unsorted_items.append(item)
            unsorted_items.sort(key=lambda i: self.frequent_itemsets[i], reverse=True) # unsorted_items now will be sorted
            if len(unsorted_items) > 0:
                self.insert_to_fptree(unsorted_items, self.root,self.headers)
                
    def insert_to_fptree(self,items,root,headers):
        for item in items:
            child=root.get_child(item)
            if( child == None):
                child=root.add_child(item)#root.children.append(FPTreeNode(item,1,root)
            else:
                 child.count=child.count+1
            if headers[item] == None:
                headers[item]=child
            else:
                current = headers[item]
                while current.link is not None:
                    if(current == child):
                        break
                    current=current.link
                current.link=child
                child.link=None
            
            root=child

##    def __init__(fp_tree,min_support,header_table):
##        self.fp_tree = fp_tree
##        self.min_support = min_support
##        self.header_table = header_table

    def generate_patterns(self):
        patterns = {}
        items = self.frequent_itemsets.keys()

        if self.root.item is None:
            suffix_value = []
        else:
            suffix_value=[self.root.item]

        for i in range(1, len(items) + 1):
            for subset in itertools.combinations(items,i):
                pattern = tuple(set(sorted(list(subset)+suffix_value)))
                patterns[pattern]=min([self.frequent_itemsets[x] for x in subset])

        return patterns

    def mine_subTrees(self):
        header_table = self.headers
        frequent_keys = self.frequent_itemsets
        patterns={}
        for key in frequent_keys:
            node = header_table[key]
            suffix = []

            while node is not None:
                suffix.append(node)
                node = node.link

            path_to_parent=[]

            fptree_input=[]
            
            for suff in suffix:
                path_to_parent=[]
                s=suff
                while s is not None:
                    if(s.item is not None):
                        path_to_parent.append(s.item)
                    s=s.parent
                for i in range(0,suff.count):
                    fptree_input.append(path_to_parent)

            fp_tree = FPTree(fptree_input, self.min_support,frequent_keys[key],key)
            pattern = fp_tree.mineFPTree()

            for p in pattern.keys():
                if p in patterns.keys():
                    patterns[p]+= pattern[p]
                else:
                    patterns[p]=pattern[p]

        return patterns

    def single_path(self,node):
        no_children = len(node.children)
        if no_children > 1:
            return False
        elif no_children == 0:
            return True
        else:
            return True and self.single_path(node.children[0])

    def mineFPTree(self):
        if(self.single_path(self.root)):
            return self.generate_patterns()
        else:
            return self.mine_subTrees()

    def getAssociationRules(self,patterns,min_confidence):

        association_rules = {}
        for freq_itemset in patterns.keys():
            right_support = patterns[freq_itemset]

            for i in range(1,len(freq_itemset)):

                for sub_pattern in itertools.combinations(freq_itemset,i):
                    left=tuple(sorted(sub_pattern))
                    right=tuple(set(freq_itemset)-set(sub_pattern))

                    if left in patterns.keys():
                        left_support = patterns[left]
                        confidence=right_support/left_support

                    if confidence>=min_confidence:
                        association_rules[left]=(right,confidence)

        return association_rules



def printFPTree(root):
    print("Printing FPTree")
    q=[]
    for i in root.children:
        q.append(i)

    while len(q)>0:
        for c in q:
            print(c.item)
            if(c.children is not None):
                for i in c.children:
                    q.append(i)
            q.remove(c)
    print("Done Printing FPTree")

#transactions=[["milk","bread","beer"],["milk","bread"],["beer","bread"]]
transactions=[["A","B","D","E"],["B","C","E"],["A","B","D","E"],["A","B","C","E"],["A","B","C","D","E"],["B","C","D"]]
fp_tree=FPTree(transactions,3,0,None)
root=fp_tree.root
fp_tree.build_tree()

#printFPTree(root)

patterns=fp_tree.mineFPTree()

print ("Patterns ",patterns)

association_rules=fp_tree.getAssociationRules(patterns,0.6)
print("Association Rules ",association_rules)