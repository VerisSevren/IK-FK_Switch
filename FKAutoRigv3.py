import maya.cmds as cmds
from math import floor
def FKAutoRig():
    #Closes windows
    if cmds.window("Rig1", q=True, ex=True):
        cmds.deleteUI("Rig1")
    if cmds.window("Rig2", q=True, ex=True):
        cmds.deleteUI("Rig2")
    #Error handeling
    if cmds.nodeType(cmds.ls(sl=True)) == None:
        message = "You must have a joint in your selection."
        cmds.warning(message)
        makeGUI2(message)
        return
    elif cmds.nodeType(cmds.ls(sl=True)) != "joint":
        message = "You must select the top joint of the chain you wish to a control rig for."
        cmds.warning(message)
        makeGUI2(message)
        return
    else:

        
        #Original Joint List
        #Also fills the list with everything below the selection
        cmds.SelectHierarchy()
        OJL = cmds.ls(sl=True)
        #FK Joint List
        FKJL = []
        IKJL = []
        count = 0
        FKHndleRatio = .5
        IKHndleRatio = 1
        anklIndex = 2 #assumes the third joint will be the ankle
        #Extra variables to make scaling the tool easier
        skipLastJoint = False
        addConstraints = True
        
        
        #Create IK/FK switch Controller
        cmds.circle(name = "IK_FK_Switch", nr = (0,1,0), c=(0,0,0), r=1)
        cmds.color(rgb=(0,1,1))
        cmds.pointConstraint(str(OJL[0]), "IK_FK_Switch")
        cmds.delete("IK_FK_Switch_pointConstraint1")
        cmds.makeIdentity("IK_FK_Switch", apply=True, t=True, r=True, s=True, n=False, pn=True)
        cmds.move(5,0,0)
        #Lock channels
        cmds.setAttr("IK_FK_Switch.sx", channelBox=False, lock=True, keyable=False)
        cmds.setAttr("IK_FK_Switch.sy", channelBox=False, lock=True, keyable=False)
        cmds.setAttr("IK_FK_Switch.sz", channelBox=False, lock=True, keyable=False)
        cmds.setAttr("IK_FK_Switch.rx", channelBox=False, lock=True, keyable=False)
        cmds.setAttr("IK_FK_Switch.ry", channelBox=False, lock=True, keyable=False)
        cmds.setAttr("IK_FK_Switch.rz", channelBox=False, lock=True, keyable=False)
        #Add IK and FK attributes
        cmds.addAttr(ln="Streatch_Tolerance", at="float", dv=0)#AddStreatchy Offset
        cmds.setAttr("IK_FK_Switch.Streatch_Tolerance", channelBox=True, l=False)
        cmds.setAttr("IK_FK_Switch.Streatch_Tolerance", k=True)
        cmds.addAttr(ln="IK", at="float", min=0, max=1, dv=0)#AddIK
        cmds.setAttr("IK_FK_Switch.IK", channelBox=True, l=False)
        cmds.setAttr("IK_FK_Switch.IK", k=True)
        cmds.addAttr(ln="FK", at="float", min=0, max=1, dv=1)#AddFK
        cmds.setAttr("IK_FK_Switch.FK", channelBox=True, l=False)
        cmds.setAttr("IK_FK_Switch.FK", k=True)
        
        
        #Creates new FK Skeleton identicle to the original skeleton
        cmds.JointTool()
        for jnt in OJL:
            rad = str(cmds.joint(OJL[count], q=True, rad=True)).replace("[","")
            newrad = rad.replace("]","")
            cmds.joint(p=cmds.xform(jnt,q=True, t=True, ws=True), rad = float(newrad))
            FKJL.append(cmds.ls(sl=True))
            count += 1
        count = 0
        maya.mel.eval("escapeCurrentTool;")
        

       #Renames, orients and colors the new FK skeleton
        for jnt in FKJL:
            FKJL[count] = cmds.rename(jnt, str(OJL[count]+"_FK_CTRL"))
            cmds.orientConstraint(str(OJL[count]),str(OJL[count]+"_FK_CTRL"))
            cmds.pointConstraint(str(OJL[count]),str(OJL[count]+"_FK_CTRL"))
            cmds.delete(OJL[count]+"_FK_CTRL_orientConstraint1", OJL[count]+"_FK_CTRL_pointConstraint1")
            cmds.select(OJL[count]+"_FK_CTRL")
            cmds.makeIdentity(apply=True, t=True, r=True, s=True, n=False, pn=True)#Freze transforms
            cmds.color(rgb=(0,0,1))
        #Sets up handles on the new FK skeleton and preps it for use    
            if count > 0:
                cmds.setAttr(FKJL[count]+".tx", channelBox=False, lock=True, keyable=False)
                cmds.setAttr(FKJL[count]+".ty", channelBox=False, lock=True, keyable=False)
                cmds.setAttr(FKJL[count]+".tz", channelBox=False, lock=True, keyable=False)
            cmds.setAttr(FKJL[count]+".sx", channelBox=False, lock=True, keyable=False)
            cmds.setAttr(FKJL[count]+".sy", channelBox=False, lock=True, keyable=False)
            cmds.setAttr(FKJL[count]+".sz", channelBox=False, lock=True, keyable=False)
            cmds.setAttr(FKJL[count]+".radi", channelBox=False, lock=True, keyable=False)
            #Adds Constraints
            if addConstraints == True:
                cmds.orientConstraint(FKJL[count], OJL[count], mo=True)
                if count < 1:
                    cmds.scaleConstraint(FKJL[count], OJL[count], mo=False)     
           #Adds Curves
            if count < len(FKJL) - 1 and skipLastJoint == False:  #Skips the final joint as it shouldn't need a controll
                rad = cmds.xform(OJL[count+1], q=True, t=True, r=True)[0]*FKHndleRatio
                cmds.circle(name = "crv_"+str(count), nr = (1,0,0), c=(0,0,0), r=rad)
                cmds.select("crv_"+str(count)+"Shape", r=True)
                cmds.select(str(OJL[count]+"_FK_CTRL"), tgl=True)
                cmds.parent(r=True, s=True)
                cmds.select("crv_"+str(count)+"Shape", r=True)
                cmds.rename("FK_"+OJL[count]+"Shape")
                cmds.color(rgb=(0,0,1))
                cmds.select("crv_"+str(count), r=True)
                cmds.delete()
                cmds.select(cl=True)
            elif count < len(FKJL) and skipLastJoint == True:
                rad = cmds.xform(OJL[count+1], q=True, t=True, r=True)[0]*FKHndleRatio
                cmds.circle(name = "crv_"+str(count), nr = (1,0,0), c=(0,0,0), r=rad)
                cmds.select("crv_"+str(count)+"Shape", r=True)
                cmds.select(str(OJL[count]+"_FK_CTRL"), tgl=True)
                cmds.parent(r=True, s=True)
                cmds.select("crv_"+str(count), r=True)
                cmds.delete()
                cmds.select(cl=True)
            count += 1
        
#////////// Now working on IK \\\\\\\\\\

        #Creates new FK Skeleton identicle to the original skeleton
        count = 0
        cmds.JointTool()
        for jnt in OJL:
            rad = str(cmds.joint(OJL[count], q=True, rad=True)).replace("[","")
            newrad = rad.replace("]","")
            cmds.joint(p=cmds.xform(jnt,q=True, t=True, ws=True), rad = float(newrad))
            IKJL.append(cmds.ls(sl=True))
            count += 1
        count = 0
        maya.mel.eval("escapeCurrentTool;")
        
        
        #Creates IK controller
        cmds.spaceLocator(p= cmds.xform(OJL[0],q=True, t=True, ws=True))
        cmds.rename("loc1")
        cmds.pointConstraint(OJL[anklIndex], "loc1")
        locPos=cmds.xform("loc1", q=True, t=True, ws=True)
        IKRad=locPos[0]+locPos[1]+locPos[2]
        IKRad=IKRad*IKHndleRatio
        cmds.delete("loc1")
        cmds.circle(name = "Leg_IK_Main_CTRL", nr = (0,1,0), c=(0,0,0), r=IKRad)
        cmds.color(rgb=(1,0,0))
        cmds.pointConstraint(OJL[anklIndex], "Leg_IK_Main_CTRL")
        cmds.delete("Leg_IK_Main_CTRL_pointConstraint1")
        cmds.makeIdentity("Leg_IK_Main_CTRL", apply=True, t=True, r=True, s=True, n=False, pn=True)
        #Renames, orients and colors the new FK skeleton
        for jnt in IKJL:
            IKJL[count] = cmds.rename(jnt, str(OJL[count]+"_IK_CTRL"))
            cmds.orientConstraint(str(OJL[count]),str(OJL[count]+"_IK_CTRL"))
            cmds.pointConstraint(str(OJL[count]),str(OJL[count]+"_IK_CTRL"))
            cmds.delete(OJL[count]+"_IK_CTRL_orientConstraint1", OJL[count]+"_IK_CTRL_pointConstraint1")
            cmds.select(OJL[count]+"_IK_CTRL")
            cmds.makeIdentity(apply=True, t=True, r=True, s=True, n=False, pn=True)#Freze transforms
            cmds.color(rgb=(1,0,0))
            #Preps IK skeliton for use    
            if count > 0:
                cmds.setAttr(IKJL[count]+".tx", channelBox=False, lock=True, keyable=False)
                cmds.setAttr(IKJL[count]+".ty", channelBox=False, lock=True, keyable=False)
                cmds.setAttr(IKJL[count]+".tz", channelBox=False, lock=True, keyable=False)
            #cmds.setAttr(IKJL[count]+".sx", channelBox=False, lock=True, keyable=False)
            #cmds.setAttr(IKJL[count]+".sy", channelBox=False, lock=True, keyable=False)
            #cmds.setAttr(IKJL[count]+".sz", channelBox=False, lock=True, keyable=False)
            cmds.setAttr(IKJL[count]+".radi", channelBox=False, lock=True, keyable=False)
            #Adds constraints
            if addConstraints == True:
                cmds.orientConstraint(IKJL[count], OJL[count], mo=True)
                cmds.scaleConstraint(IKJL[count], OJL[count], mo=False)
            count += 1
        
        
        #Creates IK solver and moves it under IK controller
        cmds.ikHandle(n="IKLeg", sj=IKJL[0], ee=IKJL[anklIndex] )
        cmds.parent("IKLeg", "Leg_IK_Main_CTRL")
        cmds.ikHandle(n="IKFoot", sj=IKJL[anklIndex], ee=IKJL[anklIndex+1] )
        cmds.parent("IKFoot", "Leg_IK_Main_CTRL")
        
        
        #Outliner cleanup
        #IK
        cmds.group(em=True, name=OJL[0]+"_IK_GRP")
        cmds.parent(str(IKJL[0]), OJL[0]+"_IK_GRP")
        cmds.parent("Leg_IK_Main_CTRL", OJL[0]+"_IK_GRP")
        #FK
        cmds.group(em=True, name=OJL[0]+"_FK_GRP")
        cmds.parent(str(FKJL[0]), OJL[0]+"_FK_GRP")
        #Move switch in outliner
        cmds.reorder("IK_FK_Switch", r = 2)
        #Hide Bound Chain
        cmds.setAttr(OJL[0]+".visibility", 0)
        
        
        #Connects constraints to IK_FK_Switch
        count = 0
        for jnt in OJL:
            cmds.connectAttr("IK_FK_Switch.IK", jnt+"_orientConstraint1."+jnt+"_IK_CTRLW1")
            cmds.connectAttr("IK_FK_Switch.FK", jnt+"_orientConstraint1."+jnt+"_FK_CTRLW0")
            if count < 1:
                cmds.connectAttr("IK_FK_Switch.IK", jnt+"_scaleConstraint1."+jnt+"_IK_CTRLW1")
                cmds.connectAttr("IK_FK_Switch.FK", jnt+"_scaleConstraint1."+jnt+"_FK_CTRLW0")
            count += 1
        cmds.connectAttr("IK_FK_Switch.FK", OJL[0]+"_FK_GRP.visibility")
        cmds.connectAttr("IK_FK_Switch.IK", OJL[0]+"_IK_GRP.visibility")
        
        
        #Creates 1-x relationship in IK/FK switch controller
        cmds.expression(s="IK_FK_Switch.FK = 1-IK_FK_Switch.IK", o="IK_FK_Switch", ae=1, uc="all")
        cmds.setAttr("IK_FK_Switch.FK", k=False, cb=False)
        
        
        #Set up Streatchy joints
        cmds.spaceLocator(n=str(OJL[0]+"_LOCATOR"))#Locator 1
        cmds.pointConstraint(str(IKJL[0]), OJL[0]+"_LOCATOR")
        cmds.spaceLocator(n=str(OJL[anklIndex]+"_LOCATOR"))#Locator2
        cmds.pointConstraint("Leg_IK_Main_CTRL", OJL[anklIndex]+"_LOCATOR")
        cmds.parent(OJL[0]+"_LOCATOR", OJL[anklIndex]+"_LOCATOR", OJL[0]+"_IK_GRP")
        
        #Get max offset distance (Streatch Tolerance)
        length1 = cmds.getAttr(OJL[1]+".translateX")
        length2 = cmds.getAttr(OJL[2]+".translateX")
        distance = length1+length2
        distance = distance*100
        distance = floor(distance) #Floor to stop snapping.
        distance = distance/100 
        cmds.setAttr("IK_FK_Switch.Streatch_Tolerance", distance)
        cmds.createNode("distanceBetween", n=OJL[0]+"_distanceBetween")#DistanceBetween
        cmds.connectAttr(OJL[0]+"_LOCATOR.translate", OJL[0]+"_distanceBetween.point1")
        cmds.connectAttr(OJL[anklIndex]+"_LOCATOR.translate", OJL[0]+"_distanceBetween.point2")
        
        #Create condition logic
        cmds.createNode("condition", n=OJL[0]+"_streatchCondition")#Create <= Condition
        cmds.setAttr(OJL[0]+"_streatchCondition.operation", 3)
        cmds.connectAttr(OJL[0]+"_distanceBetween.distance", OJL[0]+"_streatchCondition.firstTerm")
        cmds.connectAttr(OJL[0]+"_distanceBetween.distance", OJL[0]+"_streatchCondition.colorIfTrueR")
        cmds.setAttr(OJL[0]+"_streatchCondition.secondTerm", distance)
        cmds.setAttr(OJL[0]+"_streatchCondition.colorIfFalseR", distance)
        
        #Create streatch fraction
        cmds.createNode("multiplyDivide", n=OJL[0]+"_streatchFraction")
        cmds.connectAttr(OJL[0]+"_streatchCondition.outColorR", OJL[0]+"_streatchFraction.input1X")
        cmds.setAttr(OJL[0]+"_streatchFraction.input2X", distance)
        cmds.setAttr(OJL[0]+"_streatchFraction.operation", 2)
        
        #Create inverse fraction
        cmds.createNode("multiplyDivide", n=OJL[0]+"_inverseFraction")
        cmds.connectAttr(OJL[0]+"_streatchFraction.outputX", OJL[0]+"_inverseFraction.input2X")
        cmds.setAttr(OJL[0]+"_inverseFraction.input1X", 1)
        cmds.setAttr(OJL[0]+"_inverseFraction.operation", 2)
        
        #Connect first 2 joints
        count = 0
        while count < anklIndex:
            cmds.connectAttr(OJL[0]+"_streatchFraction.outputX", IKJL[count]+".scaleX")
            cmds.connectAttr(OJL[0]+"_inverseFraction.outputX", IKJL[count]+".scaleY")
            cmds.connectAttr(OJL[0]+"_inverseFraction.outputX", IKJL[count]+".scaleZ")
            count += 1
        
        
        
        
        print "Now you have an awesome rig!"        

        
#Default window        
def makeGUI1():
    if cmds.window("Rig1", q=True, ex=True):
       cmds.deleteUI("Rig1")
    if cmds.window("Rig2", q=True, ex=True):
        cmds.deleteUI("Rig2")
   
    cmds.window("Rig1", title = "IKFK", w=200)
    cmds.columnLayout(adjustableColumn=True)
    cmds.text( label=" ")
    cmds.text( label="Select the top joint of a joint chain.", align="center")
    cmds.text( label=" ")
    cmds.text( label=" ")
    cmds.text( label=" ")
    cmds.button (label="Rig!", w=150, c="FKAutoRig()")
   
    cmds.showWindow ("Rig1")

#Error window
def makeGUI2(string):
    if cmds.window("Rig2", q=True, ex=True):
       cmds.deleteUI("Rig2")
   
    cmds.window("Rig2", title = "IKFK", w=200)
    cmds.columnLayout(adjustableColumn=True)
    cmds.text( label=" ")
    cmds.text( label="ERROR:", align="left")
    cmds.text( label=" ")
    cmds.text( label=string, align="left")
    cmds.text( label=" ")
    cmds.text( label=" ")
    cmds.text( label=" ")
    cmds.button (label="OK", w=150, c="makeGUI1()")
   
    cmds.showWindow ("Rig2")
   
makeGUI1()         