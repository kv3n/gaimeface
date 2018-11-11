// Fill out your copyright notice in the Description page of Project Settings.

#include "GaimeFaceGameModeBase.h"
#include "Gaimer.h"

AGaimeFaceGameModeBase::AGaimeFaceGameModeBase()
{
	DefaultPawnClass = AGaimer::StaticClass();
}